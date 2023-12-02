from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models import Product, ProductColorAndSizeValue, Order, OrderItem


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
