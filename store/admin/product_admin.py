from django.contrib import admin
from django.db.models import Count
from django.shortcuts import reverse
from django.utils.http import urlencode
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.forms import Textarea
from django.db import models

from mptt.admin import MPTTModelAdmin
from jalali_date.admin import ModelAdminJalaliMixin

from ..models import (Category, Product, ProductSpecification, ProductSpecificationValue, ProductColor,
                      ProductSize,)
from ..forms import ProductFormAdmin


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'products_count')
    search_fields = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(produc_count=Count('products'))

    def products_count(self, obj):
        url = (reverse('admin:store_product_changelist') + '?' + urlencode({'category': obj.pk}))
        return format_html('<a href="{}">{}</a>', url, obj.produc_count)


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    fields = ('name',)
    search_fields = ('name',)


class ProductSpecificationValueTabu(admin.TabularInline):
    model = ProductSpecificationValue
    fields = ('specification', 'value',)
    autocomplete_fields = ('specification',)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'cols': 70, 'rows': 4})}
    }
    extra = 1


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    fields = ('name', 'color')
    list_display = ('name', 'color', 'color_image')
    search_fields = ('color', 'name')

    def color_image(self, obj):
        return format_html('<div style="background-color: {}; width: 20px; height: 20px;"></div>', obj.color)


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    fields = ('size',)
    list_display = ('size',)
    search_fields = ('size',)


@admin.register(Product)
class ProductAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    form = ProductFormAdmin
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'description', 'short_description', 'category')
        }),
        (_('Pricing'), {
            'fields': ('price', 'discount', 'discount_price', 'discount_timer')
        }),
        (_('Inventory and Slug'), {
            'fields': ('inventory', 'slug_change', 'slug')
        }),
        (_('Status and Timestamps'), {
            'fields': ('is_active', 'datetime_created', 'datetime_updated')
        }),
    )
    readonly_fields = ('datetime_created', 'datetime_updated',)
    inlines = (ProductSpecificationValueTabu,)
    list_display = ('title', 'price', 'datetime_created', 'datetime_updated', 'is_active')
    ordering = ('-datetime_updated',)
    search_fields = ('title',)
    autocomplete_fields = ('category',)
