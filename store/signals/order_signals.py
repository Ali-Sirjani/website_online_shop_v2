from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from ..models import Product, ProductColorAndSizeValue, Order, OrderItem, Coupon
from ..cart import Cart


@receiver(user_logged_in)
def add_item_to_cart_from_session(sender, user, request, **kwargs):
    if request.session.get('cart'):
        coupon_dict = request.session.get('coupon')
        coupon = None
        if coupon_dict:
            try:
                coupon = Coupon.objects.get(pk=coupon_dict.get('coupon_pk'))

            except Coupon.DoesNotExist:
                pass

        cart = Cart(request)
        order, create = Order.objects.get_or_create(customer=user, completed=False)
        order.coupon = coupon
        order.save()
        for item_session in cart:
            product = item_session.get('product')

            if product.is_active:
                item, create = OrderItem.objects.get_or_create(
                    product=item_session['product'],
                    color_size=item_session.get('color_size'),
                    order=order,
                )

                if create:
                    item.quantity = item_session['quantity']
                    item.save()

                else:
                    item.quantity += item_session['quantity']
                    item.save()

        messages.success(request, _('The product add to your cart'))
        cart.clear_cart()


@receiver(user_logged_in)
def set_user_for_order_with_customer_null(sender, user, request, **kwargs):
    orders_with_user_email_completed = Order.objects.filter(customer=None, email=user.email, completed=True)

    if orders_with_user_email_completed.exists():
        orders_with_user_email_completed.update(customer=user)

    orders_with_user_email_uncompleted = Order.objects.filter(customer=None, email=user.email, completed=False)

    if orders_with_user_email_uncompleted.exists():
        order_items = OrderItem.objects.filter(order__in=orders_with_user_email_uncompleted)
        order_items.delete()
        orders_with_user_email_uncompleted.delete()


@receiver(post_save, sender=Product)
def remove_inactive_product_from_order_items(sender, instance, **kwargs):
    if not instance.is_active:
        # Get all OrderItems that reference this product and belong to orders where 'completed' is False
        orders_to_update = Order.objects.filter(
            items__product=instance, completed=False
        )

        if orders_to_update.exists():
            for order in orders_to_update:
                order_item_to_delete = order.items.filter(product=instance)
                order_item_to_delete.delete()


@receiver(post_save, sender=ProductColorAndSizeValue)
def delete_inactive_product_color_size_in_order_itme(sender, instance, *args, **kwargs):
    if (instance.inventory and instance.inventory <= 0) or (not instance.is_active):
        order_items = OrderItem.objects.filter(color_size=instance, order__completed=False)
        order_items.delete()
