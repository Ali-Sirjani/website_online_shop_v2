from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField

from .product_models import Product
from ..utils import generate_coupon_code


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, default=generate_coupon_code, verbose_name=_('coupon code'))
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('start date'))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('end date'))
    num_available = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('number available'))
    num_used = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('number used'))

    is_active = models.BooleanField(default=True, verbose_name=_('active'))

    def is_valid(self):
        start_date = self.start_date
        end_date = self.end_date
        num_available = self.num_available
        num_used = self.num_used

        if start_date and num_available:
            return (start_date <= timezone.now() <= end_date) and (num_available > num_used)

        elif start_date:
            return start_date <= timezone.now() <= end_date

        elif num_available:
            return num_available > num_used

        return False

    def __str__(self):
        return f'{self.code}'


class CouponRule(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='rules', verbose_name=_('coupon'))
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('discount percentage'))
    start_price = models.PositiveIntegerField(verbose_name=_('start price'))

    def apply_discount(self, order_total):
        if order_total >= self.start_price:
            discount_amount = (self.discount_percentage / 100) * order_total
            return discount_amount
        return 0

    def __str__(self):
        return f"{self.coupon} - {self.discount_percentage}% off if order total is >= {self.start_price}"
