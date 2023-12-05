from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField


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


class TopTag(models.Model):
    LEVEL_CHOICES = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
    )

    tag = models.OneToOneField(Tag, on_delete=models.CASCADE, related_name='top_tags', verbose_name=_('tag'))

    level = models.CharField(max_length=1, choices=LEVEL_CHOICES,
                             help_text=_('Levels are ordered from top to bottom, with 1 being the highest.'),
                             verbose_name=_('level'))
    is_top_level = models.BooleanField(default=False,
                                       help_text='Check this box if you want the product to be at the top of its specified level.',
                                       verbose_name='is_top_level')

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    class Meta:
        verbose_name = _('top tag')
        verbose_name_plural = _('top tags')

    def __str__(self):
        return f'{self.tag}'


class ActivePostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(can_published=True)


class Post(models.Model):
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('tags'))
    author = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, verbose_name=_('author'))

    title = models.CharField(max_length=250, verbose_name=_('title'))
    description = RichTextField(verbose_name=_('description'))
    image = models.ImageField(upload_to='post_images/', null=True, verbose_name=_('image'))
    can_published = models.BooleanField(default=True, verbose_name=_('can published'))
    slug_change = models.BooleanField(verbose_name=_('slug change'), help_text=_('If you want change the slug by name'))
    slug = models.SlugField(unique=True, allow_unicode=True, blank=True, max_length=300, verbose_name=_('slug'),
                            help_text=_('If field be empty it\'s automatic change by name '))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    objects = models.Manager()
    active_objs = ActivePostManager()

    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')

    def __str__(self):
        return f'{self.title}'


class PostComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments', verbose_name=_('post'))
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='post_comments',
                               verbose_name=_('author'))

    text = models.TextField(verbose_name=_('text'))

    confirmation = models.BooleanField(default=False, verbose_name=_('confirmation'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    class Meta:
        verbose_name = _('post comment')
        verbose_name_plural = _('post comments')

    def __str__(self):
        return f'{self.author}'
