from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core import serializers

from allauth.account.forms import ChangePasswordForm, SetPasswordForm

from .models import Profile
from .forms import ProfileForm, ContactUsForm
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


class ProfileView(LoginRequiredMixin, generic.UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'core/profile.html'
    success_url = reverse_lazy('core:profile')
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        profile_user, create = Profile.objects.get_or_create(user=self.request.user)
        return profile_user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.has_usable_password():
            context['change_pass_form'] = ChangePasswordForm()
        else:
            context['set_pass_form'] = SetPasswordForm()

        context['orders_completed'] = Order.objects.filter(customer=self.request.user, completed=True).order_by(
            '-datetime_payed').prefetch_related('items')

        return context


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
