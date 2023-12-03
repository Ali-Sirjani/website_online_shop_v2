from django.contrib import admin
from django.forms import Textarea
from django.db.models import TextField
from django.utils.translation import gettext_lazy as _

from .models import Tag, Post, PostComment


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'datetime_created', 'datetime_updated')
    search_fields = ('name',)
    ordering = ('datetime_updated',)


class PostCommentInline(admin.TabularInline):
    model = PostComment
    readonly_fields = ('datetime_updated',)
    fields = ('author', 'text', 'confirmation', 'datetime_updated')
    ordering = ('-datetime_updated',)
    extra = 1
    autocomplete_fields = ('author',)
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'cols': 70, 'rows': 4})}
    }
