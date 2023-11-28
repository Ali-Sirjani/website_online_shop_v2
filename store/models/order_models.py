from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField

from .product_models import Product, ProductColorAndSizeValue
from ..utils import generate_coupon_code


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, default=generate_coupon_code, verbose_name=_('coupon code'))
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_('start date'))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_('end date'))
    num_available = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('number available'))
    num_used = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('number used'))
    reason_make = models.TextField(verbose_name=_('reason make'))

    is_active = models.BooleanField(default=True, verbose_name=_('active'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime ordered'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

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

    class Meta:
        unique_together = ('coupon', 'discount_percentage', 'start_price')

    def apply_discount(self, order_total):
        if order_total >= self.start_price:
            discount_amount = (self.discount_percentage / 100) * order_total
            return discount_amount
        return 0

    def __str__(self):
        return f'{self.coupon} - {self.discount_percentage}% off if order total is >= {self.start_price}'


class Order(models.Model):
    customer = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='orders', null=True,
                                 blank=True, verbose_name=_('customer'))

    first_name = models.CharField(max_length=200, verbose_name=_('first name'))
    last_name = models.CharField(max_length=200, verbose_name=_('last name'))
    email = models.EmailField(max_length=254, null=True, verbose_name=_('email'))
    phone = PhoneNumberField(null=True, region='IR', verbose_name=_('phone'))
    order_note = models.TextField(blank=True, verbose_name=_('order note'))
    completed = models.BooleanField(default=False, blank=True, verbose_name=_('completed'))
    tracking_code = models.CharField(max_length=200, blank=True, verbose_name=_('tracking code'))
    datetime_payed = models.DateTimeField(null=True, blank=True, verbose_name=_('datetime payed'))
    datetime_delivered = models.DateTimeField(null=True, blank=True, verbose_name=_('datetime delivered'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime ordered'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    def __str__(self):
        return f'{self.pk}'

    @property
    def get_cart_items(self):
        return sum([item.quantity for item in self.items.all()])

    get_cart_items.fget.short_description = _('Cart Items')

    @property
    def get_cart_total_no_discount(self):
        return sum([item.get_total_no_discount for item in self.items.all()])

    get_cart_total_no_discount.fget.short_description = _('Cart Total (No Discount)')

    @property
    def get_cart_total_with_discount(self):
        return sum([item.get_total_with_discount for item in self.items.all()])

    get_cart_total_with_discount.fget.short_description = _('Cart Total (With Discount)')

    @property
    def get_cart_total_profit(self):
        return sum([item.get_total_profit for item in self.items.all()])

    get_cart_total_profit.fget.short_description = _('Cart Total Profit')

    @property
    def get_cart_total(self):
        return self.get_cart_total_no_discount - self.get_cart_total_profit

    get_cart_total.fget.short_description = _('Cart Total')

    @property
    def avg_track_items(self):
        try:
            avg = sum([item.track_order for item in self.items.all()]) / len(self.items.all())
        except ZeroDivisionError:
            return _('zero')
        if avg == 0:
            return _('Unpaid')
        if 0 < avg <= 20:
            return _('Paid')
        if 21 <= avg <= 40:
            return _('Processing')
        if 41 <= avg <= 99:
            return _('Out for delivery')
        if avg == 100:
            return _('Delivered')

    avg_track_items.fget.short_description = _('Average Track Items')


class OrderItem(models.Model):
    TRACK_ORDER_UNPAID = 0
    TRACK_ORDER_PAYED = 20
    TRACK_ORDER_PROCESSING = 40
    TRACK_ORDER_OUT_DELIVERY = 80
    TRACK_ORDER_DELIVERED = 100
    TRACK_ORDER_CHOICES = (
        (TRACK_ORDER_UNPAID, 'Unpaid'),
        (TRACK_ORDER_PAYED, 'Payed'),
        (TRACK_ORDER_PROCESSING, 'Processing'),
        (TRACK_ORDER_OUT_DELIVERY, 'Out for delivery'),
        (TRACK_ORDER_DELIVERED, 'Delivered'),
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items',
                                verbose_name=_('product'))
    color_size = models.ForeignKey(ProductColorAndSizeValue, on_delete=models.PROTECT, null=True, blank=True,
                                   related_name='color_size_items', verbose_name=_('color and size'))
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='items', verbose_name=_('order'))

    quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1)], verbose_name=_('quantity'))
    track_order = models.PositiveSmallIntegerField(default=TRACK_ORDER_UNPAID, blank=True, choices=TRACK_ORDER_CHOICES,
                                                   verbose_name=_('track order'))
    datetime_processing = models.DateTimeField(null=True, blank=True, verbose_name=_('datetime processing'))
    datetime_process_finished = models.DateTimeField(null=True, blank=True, verbose_name=_('datetime process finished'))
    # product info
    price = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('price'))
    discount = models.BooleanField(default=False, verbose_name=_('discount'))
    discount_price = models.PositiveIntegerField(blank=True, null=True, verbose_name=_('discount price'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    class Meta:
        ordering = ('datetime_created',)
        unique_together = (('product', 'color_size', 'order'), ('product', 'order'))

    def __str__(self):
        return f'order number: {self.order.pk}'

    @property
    def get_total_no_discount(self):
        if self.price:
            return self.price * self.quantity
        return 0

    get_total_no_discount.fget.short_description = _('Total (No Discount)')

    @property
    def get_total_with_discount(self):
        if self.discount:
            return self.discount_price * self.quantity
        return 0

    get_total_with_discount.fget.short_description = _('Total (With Discount)')

    @property
    def get_total_profit(self):
        if self.discount:
            return self.get_total_no_discount - self.get_total_with_discount
        return 0

    get_total_profit.fget.short_description = _('Total Profit')

    @property
    def get_total(self):
        return self.get_total_no_discount - self.get_total_profit

    get_total.fget.short_description = _('Total')


class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, related_name='address', null=True,
                                 verbose_name=_('order'))

    state = models.CharField(max_length=200, verbose_name=_('state'))
    city = models.CharField(max_length=200, verbose_name=_('city'))
    address = models.TextField(verbose_name=_('address'))
    plate = models.PositiveSmallIntegerField(verbose_name=_('plate'))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('datetime created'))
    datetime_updated = models.DateTimeField(auto_now=True, verbose_name=_('datetime updated'))

    def __str__(self):
        return f'{self.address}'
