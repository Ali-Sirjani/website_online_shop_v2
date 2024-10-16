from math import floor

from django.db import models
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey
from ckeditor.fields import RichTextField
from colorfield.fields import ColorField


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

    def get_absolute_url(self):
        return reverse('store:category_page', args=[self.slug])


class ActiveProductsManager(models.Manager):
    def get_queryset(self):
        return super(ActiveProductsManager, self).get_queryset().filter(is_active=True, inventory__gt=0)


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
    inventory = models.IntegerField(default=0, verbose_name=_('inventory'))
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

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    def active_color_size(self):
        return self.color_size_values.filter(models.Q(inventory__gt=0) | models.Q(inventory=None), is_active=True)

    def color_dict(self):
        query = self.color_size_values.all()
        color_dict = {}

        for color_size in query:
            if color_size.color and color_size.is_active and (color_size.inventory is None or color_size.inventory > 0):
                color_dict[str(color_size.color.pk)] = color_size.color

        return color_dict

    def size_dict(self):
        query = self.color_size_values.all()
        color_dict = {}

        for color_size in query:
            if color_size.size and color_size.is_active and (color_size.inventory is None or color_size.inventory > 0):
                color_dict[str(color_size.size.pk)] = color_size.size

        return color_dict

    def main_image(self):
        for image in self.images.all():
            if image.is_main:
                return image.image.url

        return None

    def avg_star(self):
        half_star = False

        try:
            comments = self.comments.all()
            confirmed_comments_star = [int(comment.star) for comment in comments if comment.confirmation]
            comments_len = len(confirmed_comments_star)
            avg = sum(confirmed_comments_star) / comments_len
        except ZeroDivisionError:
            full_star = 0
            return full_star, half_star, 0

        if avg % 1 >= 0.5:
            half_star = True

        full_star = floor(avg)

        return full_star, half_star, comments_len


class ProductSpecification(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('name'))

    class Meta:
        verbose_name = _('product specification')
        verbose_name_plural = _('product specifications')

    def __str__(self):
        return f'{self.name}'


class ProductSpecificationValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specs_values',
                                verbose_name=_('product'))
    specification = models.ForeignKey(ProductSpecification, on_delete=models.CASCADE, related_name='specs_values',
                                      verbose_name=_('specification'))

    value = models.TextField(verbose_name=_('value'))

    class Meta:
        unique_together = ('product', 'specification')
        verbose_name = _('product specification value')
        verbose_name_plural = _('product specification values')

    def __str__(self):
        return f'{self.value}'


class ProductColor(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_('name'))
    color = ColorField(unique=True, verbose_name=_('color'))

    class Meta:
        verbose_name = _('product color')
        verbose_name_plural = _('product colors')

    def __str__(self):
        return f'{self.name}'


class ProductSize(models.Model):
    size = models.CharField(max_length=200, unique=True, verbose_name=_('size'))

    class Meta:
        verbose_name = _('product size')
        verbose_name_plural = _('product sizes')

    def __str__(self):
        return f'{self.size}'


class ActiveProductColorAndSizeValueManager(models.Manager):
    def get_queryset(self):
        return super(ActiveProductColorAndSizeValueManager, self).get_queryset().filter(
            models.Q(inventory=None) | models.Q(inventory__gt=0), is_active=True)


class ProductColorAndSizeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='color_size_values',
                                verbose_name=_('product'))
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE, null=True, blank=True,
                              related_name='color_size_values', verbose_name=_('color'))
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, null=True, blank=True,
                             related_name='color_size_values', verbose_name=_('size'))

    additional_cost = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('additional cost'))
    inventory = models.IntegerField(null=True, blank=True, verbose_name=_('inventory'))
    is_active = models.BooleanField(default=True, verbose_name=_('active'))

    objects = models.Manager()
    active_objs = ActiveProductColorAndSizeValueManager()

    class Meta:
        unique_together = (('color', 'size', 'product'),)
        verbose_name = _('product color and size value')
        verbose_name_plural = _('product color and size values')

    def __str__(self):
        color_size_str = 'None'
        color = self.color
        size = self.size
        if color and size:
            color_size_str = f'{color}--{size}'

        elif color:
            color_size_str = f'{color}'

        elif size:
            color_size_str = f'{size}'

        return color_size_str


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images',
                                verbose_name=_('product'))

    image = models.ImageField(upload_to='product_images/', verbose_name=_('image'))
    is_main = models.BooleanField(default=False, verbose_name=_('is main'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')
        ordering = ('-is_main',)

    def __str__(self):
        return f'{self.pk}'


class ActiveTopProductsManager(models.Manager):
    def get_queryset(self):
        return super(ActiveTopProductsManager, self).get_queryset().filter(product__is_active=True,
                                                                           product__inventory__gt=0)


class TopProduct(models.Model):
    LEVEL_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    )
    LIMIT_CHOICES_TO_PRODUCT = {'is_active': True, 'inventory__gt': 0}

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='top_products',
                                   limit_choices_to=LIMIT_CHOICES_TO_PRODUCT, verbose_name=_('product'))

    level = models.CharField(max_length=1, choices=LEVEL_CHOICES,
                             help_text=_('Levels are ordered from top to bottom, with 1 being the highest.'),
                             verbose_name=_('level'))
    is_top_level = models.BooleanField(default=False,
                                       help_text='Check this box if you want the product to be at the top of its specified level.',
                                       verbose_name='is_top_level')

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    objects = models.Manager()
    active_objs = ActiveTopProductsManager()

    class Meta:
        verbose_name = _('top product')
        verbose_name_plural = _('top products')

    def __str__(self):
        return f'{self.product}'

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.product.slug])


class ProductComment(models.Model):
    STAR_CHOICES = (
        ('1', _('Too Bad')),
        ('2', _('Bad')),
        ('3', _('Normal')),
        ('4', _('Good')),
        ('5', _('Great')),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', verbose_name=_('product'))
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='comments',
                               verbose_name=_('author'))

    text = models.TextField(verbose_name=_('text'))
    star = models.CharField(max_length=1, choices=STAR_CHOICES, verbose_name=_('star'))

    confirmation = models.BooleanField(default=False, verbose_name=_('confirmation'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    class Meta:
        verbose_name = _('product comment')
        verbose_name_plural = _('product comments')

    def __str__(self):
        return f'{self.author}'

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.product.slug])
