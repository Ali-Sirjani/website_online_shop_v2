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
