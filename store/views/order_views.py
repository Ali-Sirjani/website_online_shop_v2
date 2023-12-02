import json

from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.contrib import messages

from ..models import Order, OrderItem, Product, ProductColor, ProductSize, ProductColorAndSizeValue, Coupon
from ..cart import Cart
from .. import utils
from ..forms import CouponForm


def update_color_size_drop(request):
    user = request.user
    if user.is_authenticated and (user.is_staff or user.is_superuser):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            messages.warning(request, _('Oops! Something went wrong with your request. Please try again.'
                                        ' If the issue persists, contact our support team for assistance.'))
            return JsonResponse('Something went wrong', safe=False)

        product_pk = data.get('productId')

        if product_pk:
            try:
                color_size_query = Product.active_objs.get(pk=product_pk).color_size_values.filter(
                    Q(inventory__gt=0) | Q(inventory=None), is_active=True, )
                data_response = {}
                for value in color_size_query:
                    data_response[str(value)] = value.pk

                return JsonResponse(data_response, safe=False)
            except Product.DoesNotExist:
                messages.error(request, _('Please enter a active product'))
                return JsonResponse('inactive product', safe=False)

        messages.error(request, _('Please enter a product'))
        return JsonResponse('Invalid pk', safe=False)


def update_item(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        messages.warning(request, _('Oops! Something went wrong with your request. Please try again.'
                                    ' If the issue persists, contact our support team for assistance.'))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    quantity = data.get('quantity')
    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 0

    if quantity != 0:
        customer = request.user

        product_id = data.get('productId')
        color = data.get('colorId')
        size = data.get('sizeId')
        color_size_pk = data.get('colorSizeId')
        action = data.get('action')

        color_obj = size_obj = product = product_color_size = None

        if action != 'delete_cart':
            product = get_object_or_404(Product.active_objs, pk=product_id, )
            if color:
                color_obj = get_object_or_404(ProductColor, pk=color, )
            if size:
                size_obj = get_object_or_404(ProductSize, pk=size, )

            try:
                if color_size_pk:
                    product_color_size = product.color_size_values.get(Q(inventory__gt=0) | Q(inventory=None),
                                                                       pk=color_size_pk, is_active=True)
                else:
                    product_color_size = product.color_size_values.get(color=color_obj, size=size_obj, is_active=True)

            except ProductColorAndSizeValue.DoesNotExist:
                if product.active_color_size().exists():
                    messages.error(request, _('Please select color or size for product!'))
                    return JsonResponse('chose color or size!', safe=False)

        if customer.is_authenticated:
            order, order_created = Order.objects.get_or_create(customer=customer, completed=False)
            if action == 'delete_cart':
                order.items.all().delete()
                messages.success(request, _('Cart deleted'))
                return JsonResponse('Cart deleted', safe=False)

            try:
                item = OrderItem.objects.get(order=order, product=product, color_size=product_color_size)
            except OrderItem.DoesNotExist:
                if quantity < 0:
                    messages.error(request, _('Please for adding product to cart enter a positive quantity!'))
                    return JsonResponse('enter valid quantity', safe=False)
                item = OrderItem.objects.create(order=order, product=product, color_size=product_color_size)

            if item.quantity * -1 > quantity or action == 'delete_item':
                item.delete()
                messages.success(request, _('Delete product'))
                return JsonResponse('Delete product', safe=False)

            elif action == 'add' and quantity > 0:
                item.quantity += quantity
                messages.success(request, _('Add product'))

            elif action == 'remove':
                if quantity < 0:
                    quantity *= -1
                item.quantity -= quantity
                if item.quantity <= 0:
                    item.delete()
                    messages.success(request, _('Delete product'))
                    return JsonResponse('Delete product', safe=False)

                else:
                    messages.success(request, _('Remove product'))

            item.save()

        else:
            cart = Cart(request)
            if action == 'delete_cart':
                cart.clear_cart()
                messages.success(request, _('Cart deleted'))
            else:
                cart.update_quantity(product_id, product_color_size, action, quantity)

        return JsonResponse('finish update view', safe=False)

    else:
        messages.warning(request, _('Please enter a correct number!'))

    return JsonResponse('finish 0', safe=False)


def cart_view(request):
    coupon_form = CouponForm(request.POST or None)
    if coupon_form.is_valid():
        try:
            coupon = Coupon.objects.get(code__exact=coupon_form.cleaned_data.get('code'))

            if coupon.can_use():
                if request.user.is_authenticated:
                    order, created = Order.objects.get_or_create(customer=request.user, completed=False)
                    order.coupon = coupon
                    order.calculate_coupon_price(request)
                    order.save()
                else:
                    order = Cart(request)
                    order.session['coupon'] = order.coupon = {'coupon_pk': coupon.pk}
                    order.calculate_coupon_price(request)
                    order.save()

            else:
                messages.error(request, _('The Coupon is not valid!'))

        except Coupon.DoesNotExist:
            messages.error(request, _('The Coupon is not valid!'))

    return render(request, 'store/order/cart.html', context={'coupon_form': coupon_form})


def checkout_view(request):
    # user with account
    if request.user.is_authenticated:
        checkout_login = utils.check_out_user_login(request)
        try:
            form_order, form_shipping, order, items = checkout_login
        except ValueError:
            return checkout_login

    # user without account
    else:
        order = cart = Cart(request)
        items = None

        checkout_anonymous = utils.check_out_user_anonymous(request, cart)
        try:
            form_order, form_shipping = checkout_anonymous
        except ValueError:
            return checkout_anonymous

    if request.method == 'GET':
        if order.calculate_coupon_price(request):
            form_order.initial['total'] = order.get_cart_total_with_coupon
        else:
            form_order.initial['total'] = order.get_cart_total

    context = {
        'order': order,
        'items': items,
        'form_order': form_order,
        'form_shipping': form_shipping,
    }

    return render(request, 'store/order/checkout.html', context)
