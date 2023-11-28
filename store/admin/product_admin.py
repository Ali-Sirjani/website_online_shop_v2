import types

from django.contrib import admin
from django.db.models import Count
from django.shortcuts import reverse
from django.utils.http import urlencode
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.forms import Textarea
from django.db import models
from django.utils.text import Truncator

from mptt.admin import MPTTModelAdmin
from jalali_date.admin import ModelAdminJalaliMixin

from ..models import (Category, Product, ProductSpecification, ProductSpecificationValue, ProductColor,
                      ProductSize, ProductColorAndSizeValue, ProductImage, TopProduct, ProductComment)
from ..forms import (ProductFormAdmin, InventoryForm, ProductColorAndSizeValueFormSetAdmin,
                     ProductImageTabuFormSetAdmin)


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


class ProductColorAndSizeValueTabu(admin.TabularInline):
    model = ProductColorAndSizeValue
    formset = ProductColorAndSizeValueFormSetAdmin
    fields = ('color', 'color_image', 'size', 'size_price', 'inventory', 'is_active')
    readonly_fields = ('color_image',)
    autocomplete_fields = ('color', 'size')
    extra = 0

    def color_image(self, obj):
        return format_html('<div style="background-color: {}; width: 20px; height: 20px;"></div>', obj.color.color)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('color', 'size')


class ProductImageTabu(admin.TabularInline):
    model = ProductImage
    formset = ProductImageTabuFormSetAdmin
    fields = ('image', 'is_main',)
    extra = 1
    min_num = 1


class ProductCommentTabu(admin.TabularInline):
    model = ProductComment
    readonly_fields = ('datetime_updated',)
    fields = ('author', 'text', 'confirmation', 'datetime_updated')
    ordering = ('-datetime_updated',)
    extra = 1
    autocomplete_fields = ('author',)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'cols': 70, 'rows': 4})}
    }


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
    inlines = (ProductSpecificationValueTabu, ProductColorAndSizeValueTabu, ProductImageTabu, ProductCommentTabu)
    list_display = ('limit_title', 'price', 'discount_price', 'inventory', 'datetime_updated', 'is_active')
    ordering = ('-datetime_updated',)
    search_fields = ('title',)
    autocomplete_fields = ('category',)

    def get_formsets_with_inlines(self, request, obj=None):
        """
        Customizes formsets and inlines for the ProductAdmin based on the presence of an existing object (obj).
        If obj is provided, it retrieves the 'inventory' from the object. Otherwise, it creates a temporary
        InventoryForm to extract the 'inventory' from the request.POST data. This 'inventory' value is then
        applied to certain formsets within the admin.

        Note: The use of lists ensures the preservation of changes since lists act as references, making them
              a preferred choice for passing variables.

        Returns:
        - result: The modified formsets and inlines.
        """
        if obj:
            inventory = obj.inventory
        else:
            # Creating a temporary InventoryForm to extract 'inventory' from request.POST data
            inv_form = InventoryForm(data={'inventory': request.POST.get('inventory')})
            if inv_form.is_valid():
                inventory = inv_form.cleaned_data.get('inventory')
            else:
                inventory = 0

        # Getting the default formsets and inlines using the super() method
        result = super().get_formsets_with_inlines(request, obj)

        if isinstance(result, types.GeneratorType):
            # Converting the generator to a tuple for further processing
            result = tuple(result)

            for formset, inline in result:
                # Applying 'inventory' to specific formsets
                if isinstance(inline, (ProductColorAndSizeValueTabu,)):
                    formset.product_inventory = inventory

            return result

        # Unpacking the result into formsets and inlines
        formsets, inlines = result
        for inline, formset in zip(inlines, formsets):
            # Applying 'inventory' to specific formsets
            if isinstance(inline, (ProductColorAndSizeValueTabu,)):
                formset.product_inventory = inventory

        return formsets, inlines

    def limit_title(self, obj):
        return Truncator(obj.title).words(15)


@admin.register(TopProduct)
class TopProductAdmin(admin.ModelAdmin):
    fields = ('product', 'level', 'is_top_level', 'datetime_created', 'datetime_updated',)
    readonly_fields = ('datetime_created', 'datetime_updated',)
    autocomplete_fields = ('product',)
    list_display = ('product', 'level', 'is_top_level')
    ordering = ('level', '-is_top_level')
    search_fields = ('products__title',)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(product__is_active=True, product__inventory__gt=0)


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    fields = ('product', 'author', 'text', 'star', 'confirmation',
              'datetime_created', 'datetime_updated',)

    list_display = ('product', 'star', 'confirmation', 'datetime_updated',)
    ordering = ('datetime_updated',)
    autocomplete_fields = ('product', 'author')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['datetime_created', 'datetime_updated', ]
        if obj:
            readonly_fields.extend(['product', 'author'])

        return readonly_fields
