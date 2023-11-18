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

from ..models import Category, Product, ProductSpecification, ProductSpecificationValue, ProductColor, ProductColorValue
from ..forms import ProductFormAdmin, ProductColorValueFormAdmin


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


class ProductColorValueTabu(admin.TabularInline):
    model = ProductColorValue
    form = ProductColorValueFormAdmin
    fields = ('color', 'color_image', 'inventory',)
    readonly_fields = ('color_image', )
    autocomplete_fields = ('color',)
    extra = 1

    def color_image(self, obj):
        return format_html('<div style="background-color: {}; width: 20px; height: 20px;"></div>', obj.color.color)


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
    inlines = (ProductSpecificationValueTabu, ProductColorValueTabu,)
    list_display = ('title', 'price', 'datetime_created', 'datetime_updated', 'is_active')
    ordering = ('-datetime_updated',)
    search_fields = ('title',)
    autocomplete_fields = ('category',)

    def save_model(self, request, obj, form, change):
        inventory = form.cleaned_data.get('inventory')
        if obj:
            obj.inventory = inventory

        else:
            form.instance.inventory = inventory

        super().save_model(request, obj, form, change)

    def get_formsets_with_inlines(self, request, obj=None):
        formsets, inlines = super().get_formsets_with_inlines(request, obj)

        for inline, formset in zip(inlines, formsets):
            if isinstance(inline, ProductColorValueTabu):
                formset.form.request_inventory = request.POST.get('inventory')

        return formsets, inlines
