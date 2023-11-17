from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey
from ckeditor.fields import RichTextField


class Category(MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    name = models.CharField(unique=True, max_length=200, verbose_name=_('name'))
    slug_change = models.BooleanField(verbose_name=_('slug change'), help_text=_('If you want change the slug by name'))
    slug = models.SlugField(allow_unicode=True, blank=True, max_length=300, verbose_name=_('slug'),
                            help_text=_('If field be empty it\'s automatic change by name '))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return f'{self.name}'


class ActiveProductsManager(models.Manager):
    def get_queryset(self):
        return super(ActiveProductsManager, self).get_queryset().filter(is_active=True)


class Product(models.Model):
    favorite = models.ManyToManyField(get_user_model(), related_name='fav_products', default=None, blank=True,
                                      verbose_name=_('favorite'))
    category = models.ManyToManyField(Category, related_name='products', default=None, blank=True,
                                      verbose_name=_('category'))

    title = models.CharField(max_length=300, verbose_name=_('title'))
    description = RichTextField(verbose_name=_('description'))
    short_description = models.CharField(max_length=300, blank=True, verbose_name=_('short description'))
    price = models.PositiveIntegerField(verbose_name=_('price'))
    discount = models.BooleanField(default=False, verbose_name=_('discount'))
    discount_price = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('discount price'))
    discount_timer = models.DateTimeField(null=True, blank=True, verbose_name=_('discount timer'))
    inventory = models.PositiveIntegerField(default=0, verbose_name=_('inventory'))
    slug_change = models.BooleanField(default=False, verbose_name=_('slug change'),
                                      help_text=_('If you want change the slug by name'))
    slug = models.SlugField(blank=True, allow_unicode=True, max_length=300, verbose_name=_('slug'),
                            help_text=_('If field be empty it\'s automatic change by name '))
    is_active = models.BooleanField(default=True, verbose_name=_('active'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    objects = models.Manager()
    active_objs = ActiveProductsManager()

    class Meta:
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self):
        return f'{self.title}'
