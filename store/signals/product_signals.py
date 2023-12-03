import random

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.text import slugify

from ..models import Product, TopProduct, Category, ProductColorAndSizeValue


def create_unique_slug(instance, create_by, slug_primitive=None):
    if instance.slug_change or slug_primitive is None:
        slug = slugify(create_by, allow_unicode=True)
    else:
        slug = slug_primitive

    ins_class = instance.__class__
    obj = ins_class.objects.filter(slug=slug)

    if obj.exists():
        instance.slug_change = False
        slug = f'{slug}-{random.choice("12345")}'
        return create_unique_slug(instance, create_by, slug)

    return slug


@receiver(pre_save, sender=Product)
def create_slug_product(sender, instance, *args, **kwargs):
    if not instance.slug or instance.slug_change:
        instance.slug = create_unique_slug(instance, instance.title)
        instance.slug_change = False


@receiver(post_save, sender=Product)
def delete_inactive_product_in_top_product(sender, instance, *args, **kwargs):
    if instance.inventory <= 0 or not instance.is_active:
        try:
            product = TopProduct.objects.get(product_id=instance.pk)
            product.delete()
        except TopProduct.DoesNotExist:
            pass


@receiver(pre_save, sender=Product)
def set_products_inactive_for_inventory(sender, instance, *args, **kwargs):
    if instance.inventory <= 0 and instance.is_active:
        instance.is_active = False


@receiver(pre_save, sender=ProductColorAndSizeValue)
def set_product_color_size_value_as_inactive(sender, instance, *args, **kwargs):
    if (type(instance.inventory) is int) and (instance.inventory <= 0):
        instance.is_active = False


@receiver(pre_save, sender=Category)
def create_slug_category(sender, instance, *args, **kwargs):
    if not instance.slug or instance.slug_change:
        instance.slug = create_unique_slug(instance, instance.name)
        instance.slug_change = False
