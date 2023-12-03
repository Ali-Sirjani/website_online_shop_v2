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


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    fieldsets = (
        (_('Post Information'), {
            'fields': ('title', 'description', 'author', 'tags', 'can_published')
        }),
        (_('Slug Settings'), {
            'classes': ('collapse',),
            'fields': ('slug_change', 'slug')
        }),
        (_('Date and Time'), {
            'classes': ('collapse',),
            'fields': ('datetime_created', 'datetime_updated'),
        }),
    )
    readonly_fields = ('author', 'datetime_created', 'datetime_updated')
    autocomplete_fields = ('tags', )
    list_display = ('title', 'author', 'can_published', 'datetime_created', 'datetime_updated')
    inlines = (PostCommentInline, )
    search_fields = ('title', 'author__username')
    list_filter = ('can_published', )
    ordering = ('datetime_updated',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user

        super().save_model(request, obj, form, change)
