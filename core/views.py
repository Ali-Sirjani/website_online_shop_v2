import json

from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core import serializers
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from allauth.account.forms import ChangePasswordForm, SetPasswordForm

from .models import Profile, ProfileAddress
from .forms import ProfileForm, ContactUsForm, ProfileAddressFrom, SetUsernameForm
from .mixins import JSONResponseMixin
from .templatetags.trans_fa import num_fa_15
from store.models import Product, TopProduct, Order, Category
from store.utils import optimize_product_query


class HomePageView(generic.ListView):
    template_name = 'core/home_page.html'
    context_object_name = 'top_products'

    def get_queryset(self):
        top_product_pk_list = TopProduct.active_objs.values_list('pk')
        product_queryset = Product.active_objs.filter(top_products__in=top_product_pk_list)

        product_queryset = optimize_product_query(product_queryset)

        product_queryset = product_queryset.order_by('top_products__level', '-top_products__is_top_level')

        return product_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['liked'] = Product.active_objs.filter(favorite=self.request.user.pk).values_list('pk', flat=True)

        random_queryset = Product.active_objs.exclude(
            pk__in=self.get_queryset().values_list('pk')).order_by('?')

        context['random_products'] = optimize_product_query(random_queryset)[:5]
        context['category_json'] = serializers.serialize("json", Category.objects.all())
        return context


class ProfileView(LoginRequiredMixin, JSONResponseMixin, generic.UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'core/profile.html'
    success_url = reverse_lazy('core:profile')
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        profile_user, create = Profile.objects.get_or_create(user=self.request.user)
        return profile_user

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, _('profile successfully updated'))
        response_data = {'success': True, 'message': 'Profile updated successfully.'}
        return self.render_to_json_response(response_data)

    def form_invalid(self, form):
        response_data = {'form': self.ajax_response_form(form)}
        return self.render_to_json_response(response_data, status=400)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.has_usable_password():
            context['change_pass_form'] = ChangePasswordForm()
        else:
            context['set_pass_form'] = SetPasswordForm()

        context['set_username_form'] = SetUsernameForm()

        context['address_form'] = ProfileAddressFrom()

        context['orders_completed'] = Order.objects.filter(customer=self.request.user, completed=True).order_by(
            '-datetime_payed').prefetch_related('items')

        return context


@login_required
@require_POST
def set_username_view(request):
    json_mixin_obj = JSONResponseMixin()

    form = SetUsernameForm(data=request.POST)
    if form.is_valid():
        user_model = get_user_model()
        username = form.cleaned_data.get('username')
        try:
            user_exist = get_user_model().objects.get(username=username)
            if request.user.username == user_exist.username:
                form.add_error('username', _('You are already using this username. Choose a different one.'))

        except user_model.DoesNotExist:
            with transaction.atomic():
                request.user.username = username
                request.user.save()
            messages.success(request, _('Username successfully changed.'))
            return json_mixin_obj.render_to_json_response({'message': 'success'})

    response_data = {'form': json_mixin_obj.ajax_response_form(form)}
    return json_mixin_obj.render_to_json_response(response_data, status=400)


class CreatProfileAddressView(LoginRequiredMixin, JSONResponseMixin, generic.CreateView):
    model = ProfileAddress
    form_class = ProfileAddressFrom
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        addresses = request.user.profile.profile_address.all()
        if len(addresses) >= 3:
            form.add_error(None, _('You can not have more than %s address') % num_fa_15('3'))
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        profile_obj = form.save(commit=False)
        profile_obj.profile = self.request.user.profile
        profile_obj.save()
        messages.success(self.request, _('Address successfully added'))
        response_data = {'success': True, 'message': 'Profile address updated successfully.'}
        return self.render_to_json_response(response_data)

    def form_invalid(self, form):
        response_data = {'form': self.ajax_response_form(form)}
        return self.render_to_json_response(response_data, status=400)


class UpdateProfileAddressView(LoginRequiredMixin, JSONResponseMixin, generic.UpdateView):
    model = ProfileAddress
    form_class = ProfileAddressFrom
    http_method_names = ('post', 'put')

    def get_object(self, queryset=None):
        pk = self.request.POST.get('pk')
        if pk:
            return get_object_or_404(self.request.user.profile.profile_address, pk=pk)
        else:
            raise Http404

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, _('Address successfully updated'))
        response_data = {'success': True, 'message': 'Profile address updated successfully.'}
        return self.render_to_json_response(response_data)

    def form_invalid(self, form):
        response_data = {'form': self.ajax_response_form(form)}
        return self.render_to_json_response(response_data, status=400)


class DeleteProfileAddressView(LoginRequiredMixin, JSONResponseMixin, generic.DeleteView):
    model = ProfileAddress
    http_method_names = ['delete']

    def get_object(self, queryset=None):
        try:
            data = json.loads(self.request.body)
            pk = data.get('pk')
            if pk:
                return get_object_or_404(self.request.user.profile.profile_address, pk=pk)
            else:
                raise Http404
        except json.JSONDecodeError:
            return self.render_to_json_response({'error': 'Invalid JSON in the request body'}, status=400)

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        message_variables = {'state': self.object.state, 'city': self.object.city}
        self.object.delete()
        messages.success(self.request, _('Address %(state)s %(city)s deleted') % message_variables)
        return self.render_to_json_response({'status': 'deleted'})


class ContactUsView(generic.CreateView):
    form_class = ContactUsForm
    context_object_name = 'form'
    template_name = 'core/contact_us.html'

    def get_success_url(self):
        messages.success(self.request, _('We will soon answer your message'))
        return reverse_lazy('store:product_list')


class AboutUsView(generic.TemplateView):
    template_name = 'core/about_us.html'


class FAQView(generic.TemplateView):
    template_name = 'core/faq.html'


class AboutProjectView(generic.TemplateView):
    template_name = 'core/about_project.html'
