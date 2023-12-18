from django.template import library
from django.core.exceptions import FieldDoesNotExist

from ..models import Order, ShippingAddress

register = library.Library()


@register.filter
def coupon_is_valid(order, request, success_message=False):

    if request.user.is_authenticated:
        return order.calculate_coupon_price(request, success_message)

    else:
        return order.calculate_coupon_price(success_message)


@register.filter
def verbose_name_order(field):
    try:
        return Order._meta.get_field(field).verbose_name
    except FieldDoesNotExist:
        return f"Verbose name for field '{field}' not found."


@register.filter
def verbose_name_shipping(field):
    try:
        return ShippingAddress._meta.get_field(field).verbose_name
    except FieldDoesNotExist:
        return f"Verbose name for field '{field}' not found."
