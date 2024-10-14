from django.shortcuts import reverse

from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Allauth success urls
    """
    def get_login_redirect_url(self, request):
        return reverse('core:home_page')

    def get_logout_redirect_url(self, request):
        return reverse('core:home_page')

    def get_email_confirmation_redirect_url(self, request):
        return reverse('core:profile')

    def get_signup_redirect_url(self, request):
        return reverse('core:profile')
