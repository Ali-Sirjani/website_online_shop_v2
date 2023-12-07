from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=254, unique=True, verbose_name='email address')


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile',
                                verbose_name=_('user'))

    first_name = models.CharField(max_length=200, blank=True, verbose_name=_('First name'))
    last_name = models.CharField(max_length=200, blank=True, verbose_name=_('Last name'))
    phone = PhoneNumberField(unique=True, blank=True, null=True, region='IR', verbose_name=_('phone'))
    picture = models.ImageField(upload_to='accounts_pictures/',
                                default='../static/img/default_account/default_profile.png', blank=True,
                                verbose_name=_('picture'))
    state = models.CharField(max_length=200, blank=True, verbose_name=_('state'))
    city = models.CharField(max_length=200, blank=True, verbose_name=_('city'))
    address = models.TextField(blank=True, verbose_name=_('address'))
    plate = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('plate'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return f'{self.user.username}'


class ContactUs(models.Model):
    full_name = models.CharField(max_length=100, verbose_name=_('full name'))
    phone = PhoneNumberField(blank=True, null=True, region='IR', verbose_name=_('phone'),
                             help_text=_('Fill in the email or mobile number'))
    email = models.EmailField(blank=True, null=True, verbose_name=_('email'),
                              help_text=_('Fill in the email or mobile number'))
    message = models.TextField(verbose_name=_('message'))
    answer = models.BooleanField(default=False, verbose_name=_('answer'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    class Meta:
        verbose_name = _('contact us')
        verbose_name_plural = _('contact us')

    def __str__(self):
        return f'{self.full_name}'
