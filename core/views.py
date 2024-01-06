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
