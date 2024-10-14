from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


def custom_lockout_response(request, credentials, *args, **kwargs):
    messages.error(request, _('You are locked for too many requests'))
    return redirect('account_login')
