from django.db import models
from django.utils.translation import gettext_lazy as _


class AbstractShippingAddress(models.Model):
    state = models.CharField(max_length=200, verbose_name=_('state'))
    city = models.CharField(max_length=200, verbose_name=_('city'))
    address = models.TextField(verbose_name=_('address'))
    plate = models.PositiveSmallIntegerField(null=True, verbose_name=_('plate'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.address}'
