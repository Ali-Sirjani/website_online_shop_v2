from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):
    pass


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile',
                                verbose_name=_('user'))

    first_name = models.CharField(max_length=200, blank=True, verbose_name=_('First name'))
    last_name = models.CharField(max_length=200, blank=True, verbose_name=_('Last name'))
    phone = PhoneNumberField(unique=True, blank=True, null=True, region='IR', verbose_name=_('phone'))
    picture = models.ImageField(upload_to='accounts_pictures/',
                                default='static/img/default_account/default_profile.png', blank=True,
                                verbose_name=_('picture'))
    state = models.CharField(max_length=200, blank=True, verbose_name=_('state'))
    city = models.CharField(max_length=200, blank=True, verbose_name=_('city'))
    address = models.TextField(blank=True, verbose_name=_('address'))
    plate = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('plate'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime updated'))

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')

    def __str__(self):
        return f'{self.user.username}'
