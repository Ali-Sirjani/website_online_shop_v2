import random

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify

from .models import Tag, Post


def create_unique_slug_for_blog(instance, create_by, slug_primitive=None):
    if instance.slug_change or slug_primitive is None:
        slug = slugify(create_by, allow_unicode=True)
    else:
        slug = slug_primitive

    ins_class = instance.__class__
    obj = ins_class.objects.filter(slug=slug)

    if obj.exists():
        instance.slug_change = False
        slug = f'{slug}-{random.choice("12345")}'
        return create_unique_slug_for_blog(instance, create_by, slug)

    return slug


@receiver(pre_save, sender=Post)
def create_slug_post(sender, instance, *args, **kwargs):
    if not instance.slug or instance.slug_change:
        instance.slug = create_unique_slug_for_blog(instance, instance.title)
        instance.slug_change = False


@receiver(pre_save, sender=Tag)
def create_slug_tag(sender, instance, *args, **kwargs):
    if not instance.slug or instance.slug_change:
        instance.slug = create_unique_slug_for_blog(instance, instance.name)
        instance.slug_change = False
