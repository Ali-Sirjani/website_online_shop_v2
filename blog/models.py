from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('name'))
    slug_change = models.BooleanField(verbose_name=_('slug change'), help_text=_('If you want change the slug by name'))
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True, max_length=300, verbose_name=_('slug'),
                            help_text=_('If field be empty it\'s automatic change by name '))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    class Meta:
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return f'{self.name}'
