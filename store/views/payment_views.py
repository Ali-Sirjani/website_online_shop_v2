import json
import requests
import datetime

from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib import messages
from django.db import transaction

from ..models import Order
from ..cart import Cart
from .. import utils


def sandbox_process_payment(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, completed=False)
        if order.get_cart_items < 0:
            messages.info(request, _('Your cart is empty!'))
            return redirect('store:products_list')

    else:
        order_pk = request.session.get('order_pk')
        if not order_pk:
            messages.info(request, _('please try again'))
            return redirect('store:products_list')
        try:
            order = Order.objects.get(pk=order_pk)
        except Order.DoesNotExist:
            messages.info(request, _('please try again'))
            return redirect('store:products_list')

    toman_total = order.get_cart_total
    rial_total = toman_total * 10

    zarinpal_url = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json'

    request_header = {
        'accept': 'application/json',
        'content-type': 'application/json',
    }

    request_data = {
        'MerchantID': 'asdfew' * 6,
        'Amount': rial_total,
        'Description': f'order:{order.tracking_code}',
        'CallbackURL': request.build_absolute_uri(reverse('store:sandbox_callback')),
    }

    res = requests.post(url=zarinpal_url, data=json.dumps(request_data), headers=request_header)
    data = res.json()
    authority = data['Authority']
    # order.zarinpal_authority = authority
    # order.save()

    if 'errors' not in data or len(data['errors']) == 0:
        return redirect(f'https://sandbox.zarinpal.com/pg/StartPay/{authority}')

    else:
        return render(request, 'store/order/success.html')


def sandbox_callback_payment(request):
    payment_authority = request.GET.get('Authority')
    payment_status = request.GET.get('Status')

    user = request.user

    if user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=user, completed=False)
    else:
        order_pk = request.session.get('order_pk')
        order, created = Order.objects.get_or_create(pk=order_pk)

    toman_total = order.get_cart_total
    rial_total = toman_total * 10

    if payment_status == 'OK':
        request_header = {
            'accept': 'application/json',
            'content-type': 'application/json',
        }

        request_data = {
            'MerchantID': 'asdfew' * 6,
            'Amount': rial_total,
            'Authority': payment_authority,
        }

        zarinpal_url_varify = 'https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentVerification.json'

        res = requests.post(url=zarinpal_url_varify, data=json.dumps(request_data), headers=request_header)
        data = res.json()

        payment_code = data['Status']

        if payment_code == 100:
            with transaction.atomic():
                if not user.is_authenticated:
                    cart_obj = Cart(request)
                    cart_obj.clear_cart()

                order.completed = True
                for item in order.items.all():
                    item.track_order = 20
                    item.save()
                    item.product.inventory -= item.quantity
                    item.product.save()
                order.datetime_payed = datetime.datetime.now()
                # order.ref_id = data['ref_id']
                # order.zarinpal_data = data
                order.save()
                return render(request, 'store/order/success.html')

        return utils.zarin_errors(request, payment_code)

    else:
        return render(request, 'store/order/fail.html')
