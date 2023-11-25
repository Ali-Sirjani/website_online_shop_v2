import datetime

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.text import Truncator

from jalali_date.admin import ModelAdminJalaliMixin

from ..models import Coupon, CouponRule, Order, OrderItem, ShippingAddress
from ..forms import OrderAdminForm, OrderItemAdminFormSet, OrderItemAdminForm, CouponAdminForm, CouponRuleAdminFormSet


class CouponRuleTabular(admin.TabularInline):
    model = CouponRule
    formset = CouponRuleAdminFormSet
    extra = 0
    min_num = 1


@admin.register(Coupon)
class CouponAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    fields = ('code', 'start_date', 'end_date', 'num_available', 'num_used', 'reason_make',
              'is_active', 'datetime_created', 'datetime_updated',)
    readonly_fields = ('datetime_created', 'datetime_updated',)
    form = CouponAdminForm
    list_display = ('code', 'reason_make')
    search_fields = ('code',)
    inlines = (CouponRuleTabular,)
    list_filter = ('is_active',)


class OrderItemStacked(admin.StackedInline):
    model = OrderItem
    formset = OrderItemAdminFormSet
    autocomplete_fields = ('product',)
    extra = 0
    min_num = 1

    def get_fields(self, request, obj=None):
        fields = ['product', 'quantity', ]

        if obj:
            fields.extend(['price', 'discount', 'discount_price', 'track_order', 'datetime_processing',
                           'datetime_process_finished'])

        return fields

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['price', 'discount', 'discount_price', 'datetime_processing', 'datetime_process_finished']

        if obj and obj.completed:
            readonly_fields.extend(['product', 'quantity'])

        return readonly_fields


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ('id', 'customer', 'phone', 'completed', 'get_cart_total')
    ordering = ('-id',)
    inlines = (OrderItemStacked,)
    list_filter = ('completed',)
    search_fields = ('tracking_code', 'id')
    autocomplete_fields = ('customer',)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items').select_related('customer')

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (_('Contact Info'), {'fields': ('customer', 'first_name', 'last_name', 'email', 'phone',)}),
        ]

        if obj:
            fieldsets.extend([
                (_('Order Info'),
                 {'fields': ('completed', 'tracking_code', 'get_cart_items', 'get_cart_total_no_discount',
                             'get_cart_total_with_discount', 'get_cart_total_profit',
                             'get_cart_total', 'avg_track_items',),
                  'classes': ('collapse',),
                  }),
                (_('Status and Timestamps'), {
                    'fields': ('datetime_created', 'datetime_updated'),
                    'classes': ('collapse',),
                }),
            ])
        else:
            fieldsets.extend([
                (_('Order Info'),
                 {'fields': ('completed',),
                  }),
            ])

        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['tracking_code', 'get_cart_items', 'get_cart_total_no_discount',
                           'get_cart_total_with_discount', 'get_cart_total_profit', 'get_cart_total', 'avg_track_items',
                           'datetime_created', 'datetime_updated', ]

        if obj:
            readonly_fields.append('customer')

        return readonly_fields

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance  # Get the saved object

        if obj and form.cleaned_data.get('completed'):

            if not obj.tracking_code:
                obj.tracking_code = datetime.datetime.now().timestamp()

            for item in obj.items.all():
                if not item.track_order:
                    item.track_order = 20
                    item.save()

            obj.datetime_payed = datetime.datetime.now()
            obj.save()


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    form = OrderItemAdminForm
    list_display = ('order', 'limit_product_title', 'quantity', 'datetime_created', 'is_order_completed')
    autocomplete_fields = ('product', 'order',)
    search_fields = ('order__id', 'order__tracking_code')
    ordering = ('-datetime_created',)

    def save_model(self, request, obj, form, change):
        is_price_changed = 'product' in form.changed_data

        if obj and not obj.price or is_price_changed:
            if obj.product:
                obj.price = obj.product.price
                obj.discount = obj.product.discount
                obj.discount_price = obj.product.discount_price

        elif form.instance and not form.instance.price or is_price_changed:
            if form.instance.product:
                form.price = form.product.price
                form.discount = form.product.discount
                form.discount_price = form.product.discount_price

        super().save_model(request, obj, form, change)

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (_('General Information'), {
                'fields': ('product', 'order', 'quantity', 'track_order'),
            }),
        ]

        if obj:
            fieldsets.extend([
                (_('Pricing'), {
                    'fields': ('price', 'discount', 'discount_price',),
                }),
                (_('Date and Time'), {
                    'fields': ('datetime_created', 'datetime_updated',),
                }),
                (_('Calculations'), {
                    'fields': ('get_total_no_discount', 'get_total_with_discount', 'get_total_profit', 'get_total',),
                }),
            ])
        return fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['price', 'discount', 'discount_price', 'datetime_created', 'datetime_updated',
                           'get_total_no_discount', 'get_total_with_discount', 'get_total_profit', 'get_total', ]

        if obj:
            if obj.order.completed:
                readonly_fields.extend(['product', 'quantity'])

            readonly_fields.append('order')

        return readonly_fields

    @admin.display(ordering='order__completed', description='completed')
    def is_order_completed(self, obj):
        try:
            return obj.order.completed
        except AttributeError:
            return None

    def limit_product_title(self, obj):
        return Truncator(obj.product.title).words(15)
