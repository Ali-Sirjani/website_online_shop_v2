import datetime

from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from ..forms import OrderForm, ShippingAddressForm
from ..models import Order, ShippingAddress


def check_out_user_login(request):
    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, completed=False)

    if order.get_cart_items == 0:
        messages.info(request, _('The Your cart is empty! Please first add some product in your cart.'))
        return redirect('store:product_list')

    shipping, create = ShippingAddress.objects.get_or_create(order=order)

    form_order = OrderForm(request.POST or None, instance=order)
    form_shipping = ShippingAddressForm(request.POST or None, instance=shipping)

    if form_order.is_valid():

        if not order.tracking_code:
            tracking_code = datetime.datetime.now().timestamp()
            form_order.instance.tracking_code = tracking_code

        # for test total
        total = None
        try:
            total = int(form_order.cleaned_data.get('total'))
        except ValueError:
            messages.error(request, _('You change the data of checkout form!'))

        if order.coupon and order.coupon.can_use():
            final_order_total = order.get_cart_total_with_coupon
        else:
            final_order_total = order.get_cart_total

        if total == final_order_total:
            form_order.save()

            if form_shipping.is_valid():
                form_shipping.save()
                return redirect('store:sandbox_process')

        else:
            messages.info(request, _('Something went wrong! Please try again.'))

    items = order.act_items().order_by('-datetime_created')

    return form_order, form_shipping, order, items
