import datetime

from django.shortcuts import redirect, render
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Prefetch

from ..forms import OrderForm, ShippingAddressForm
from ..models import Order, OrderItem, ShippingAddress, Product


def check_out_user_login(request):
    customer = request.user
    order, created = Order.objects.select_related('coupon').prefetch_related(
        Prefetch(
            'items',
            queryset=OrderItem.objects.select_related('color_size__color', 'color_size__size').all()
        ),
        Prefetch(
            'items__product',
            queryset=Product.objects.prefetch_related('images')
        )
    ).get_or_create(customer=customer, completed=False)

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

        final_order_total = None
        if order.coupon and order.calculate_coupon_price(request, success_message=False):
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


def check_out_user_anonymous(request, cart):
    if cart.get_cart_items == 0:
        messages.info(request, _('The Your cart is empty! Pleas first add some product in your cart.'))
        return redirect('store:product_list')

    form_order = OrderForm(request.POST or None)
    form_shipping = ShippingAddressForm(request.POST or None)
    if form_order.is_valid():

        email_user = form_order.cleaned_data.get('email')

        order, create = Order.objects.get_or_create(customer=None, email=email_user, completed=False,
                                                    coupon_id=cart.coupon.get('coupon_pk'))

        request.session['order_pk'] = order.pk

        orders_obj_pk = request.session.get('orders_pk_list') or []

        if not (order.pk in orders_obj_pk):
            orders_obj_pk.append(order.pk)
            request.session['orders_pk_list'] = orders_obj_pk

        total = None
        try:
            total = int(form_order.cleaned_data.get('total'))
        except ValueError:
            messages.error(request, _('You change the data of checkout form!'))

        final_order_total = None
        if cart.coupon and cart.calculate_coupon_price(success_message=False):
            final_order_total = cart.get_cart_total_with_coupon

        else:
            final_order_total = cart.get_cart_total

        if total == final_order_total:
            form_order = OrderForm(request.POST, instance=order)

            if not order.tracking_code:
                tracking_code = datetime.datetime.now().timestamp()
                form_order.instance.tracking_code = tracking_code

            form_order.save()

            # delete order items for update in save_items_and_shipping_address_user_anonymous()
            order.items.all().delete()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    color_size=item.get('color_size'),
                    quantity=item['quantity'],
                    price=item['price'],
                    discount=item['discount'],
                    discount_price=item['discount_price'],
                )

            if form_shipping.is_valid():
                shipping, create = ShippingAddress.objects.get_or_create(order=order)

                form_shipping = ShippingAddressForm(request.POST, instance=shipping)
                form_shipping.save()

                return redirect('store:sandbox_process')

        else:
            messages.info(request, _('Something went wrong! Please try again.'))

    return form_order, form_shipping


def zarin_errors(request, payment_code):
    error_messages = ''

    if payment_code == -9:
        error_messages = _('Validation error')

    if payment_code == -10:
        error_messages = _('Terminal is not valid, please check merchant_id or ip address.')

    if payment_code == -11:
        error_messages = _('Terminal is not active, please contact our support team.')

    if payment_code == -12:
        error_messages = _('To many attempts, please try again later.')

    if payment_code == -15:
        error_messages = _('Terminal user is suspend : (please contact our support team).')

    if payment_code == -16:
        error_messages = _('Terminal user level is not valid : ( please contact our support team).')

    if payment_code == -17:
        error_messages = _('Terminal user level is not valid : ( please contact our support team).')

    if payment_code == -30:
        error_messages = _('Terminal do not allow to accept floating wages.')

    if payment_code == -31:
        error_messages = _('Terminal do not allow to accept wages, please add default bank account in panel.')

    if payment_code == -32:
        error_messages = _('Wages is not valid, Total wages(floating) has been overload max amount.')

    if payment_code == -33:
        error_messages = _('Wages floating is not valid.')

    if payment_code == -34:
        error_messages = _('Wages is not valid, Total wages(fixed) has been overload max amount.')

    if payment_code == -35:
        error_messages = _('Wages is not valid, Total wages(floating) has been reached the limit in max parts.')

    if payment_code == -40:
        error_messages = _('Invalid extra params, expire_in is not valid.')

    if payment_code == -50:
        error_messages = _('Session is not valid, amounts values is not the same.')

    if payment_code == -51:
        error_messages = _('Session is not valid, session is not active paid try.')

    if payment_code == -52:
        error_messages = _('Oops!!, please contact our support team')

    if payment_code == -53:
        error_messages = _('Session is not this merchant_id session')

    if payment_code == -54:
        error_messages = _('Invalid authority.')

    if payment_code == 101:
        error_messages = _('Verified')

    messages.warning(request, f'{error_messages}')
    return render(request, 'store/payment/fail.html')
