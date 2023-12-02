from django.contrib import messages
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from .models import Product, ProductColorAndSizeValue


class Cart:

    def __init__(self, request):
        """
        Initializes a new shopping cart instance.

        Args:
            request: The Django request object associated with the user session.

        The shopping cart is stored in the user's session, and if a cart already
        exists, inactive items are removed to ensure consistency. The cart is then
        either created or retrieved from the session.
        """
        self.request = request
        self.session = request.session

        cart = self.session.get('cart')
        if not cart:
            self.cart = self.session['cart'] = {}
        else:
            self.cart = cart
            self.remove_inactive_items()

        coupon = self.session.get('coupon')
        if not coupon:
            self.coupon = self.session['coupon'] = {}
        else:
            self.coupon = coupon

        self.save()

    def save(self):
        """
        Save the current state of the shopping cart.

        This method marks the user's session as modified, indicating that changes
        have been made to the shopping cart. This ensures that the updated cart
        information is persisted between requests.
        """
        self.session.modified = True

    def remove_inactive_items(self):
        """
        Remove inactive products and associated color-size combinations from the cart.

        This method ensures the shopping cart remains consistent by removing items
        associated with products that are no longer active. Additionally, it removes
        color-size combinations with zero inventory or those marked as inactive.
        The updated cart state is then saved.
        """
        products_pk = self.cart.keys()
        dict_pk = Product.objects.filter(id__in=products_pk).values('pk', 'is_active')
        # cart_products = Product.objects.filter(id__in=products_pk)

        for product_dict in dict_pk:
            if not product_dict['is_active']:
                del self.cart[str(product_dict['pk'])]

            else:
                key_pks = [key for key in self.cart[str(product_dict['pk'])].keys() if key != 'None']

                delete_key_list = ProductColorAndSizeValue.objects.filter(Q(inventory__lte=0) | Q(is_active=False),
                                                                          pk__in=key_pks).values_list('pk')

                for key in delete_key_list:
                    key_in_cart = str(key[0])
                    del self.cart[str(product_dict['pk'])][key_in_cart]

                del delete_key_list

        self.save()

    def set_price_item(self, item, product_pk, product_color_size_pk):
        """
        Set the price-related information for a specific item in the shopping cart.

        Args:
            item: The dictionary representing the item in the cart.
            product_pk: The primary key of the associated product.
            product_color_size_pk: The primary key of the color and size information,
                                  or 'None' if there is no specific color and size.

        This method calculates and sets the price-related information, including the
        base price, discount, and discounted price for the given item. Additional costs,
        if any (e.g., size-specific prices), are considered in the calculation.
        """
        product_obj = get_object_or_404(Product.active_objs, pk=product_pk)

        additional_cost = 0
        if product_color_size_pk != 'None':
            color_size_obj = get_object_or_404(ProductColorAndSizeValue, pk=product_color_size_pk)
            if color_size_obj.size_price:
                additional_cost = color_size_obj.size_price

        item['price'] = product_obj.price + additional_cost
        item['discount'] = product_obj.discount
        item['discount_price'] = product_obj.discount_price
        if product_obj.discount_price:
            item['discount_price'] = product_obj.discount_price + additional_cost

    def update_quantity(self, product_pk, product_color_size, action, quantity=1):
        """
        Update the quantity of a product in the shopping cart.

        Args:
            product_pk: The primary key of the product to update.
            product_color_size: The color and size information for the product, or None.
            action: The action to perform ('add', 'remove', 'delete_item').
            quantity: The quantity to add, remove, or set. Defaults to 1.

        This method allows for dynamic updates to the quantity of a product in the
        shopping cart based on the specified action. It considers various scenarios
        such as addition, removal, and deletion of items. Messages are used to notify
        the user about the performed action, and the cart state is saved.

        Example of cart item structure:
        {
            product_pk_str: {
                product_color_size_pk or 'None': {
                    'quantity': 12,
                    'price': product.price,
                    'discount': product.discount,
                    'discount_price': product.discount_price
                }
            }
        }
        """
        product_pk_str = str(product_pk)

        if product_color_size:
            product_color_size_pk = str(product_color_size.pk)
        else:
            product_color_size_pk = str(product_color_size)

        if product_pk_str not in self.cart:
            if quantity < 0:
                return
            self.cart[product_pk_str] = {}

        cart_product = self.cart[product_pk_str]

        if product_color_size_pk not in cart_product:
            cart_product[product_color_size_pk] = {'quantity': quantity}
            self.set_price_item(cart_product[product_color_size_pk], product_pk_str, product_color_size_pk)

        if cart_product[product_color_size_pk]['quantity'] * -1 > quantity or action == 'delete_item':
            del cart_product[product_color_size_pk]
            messages.success(self.request, _('Delete product'))
            self.save()
            return

        elif action == 'add':
            cart_product[product_color_size_pk]['quantity'] += quantity
            messages.success(self.request, _('Add product'))

        elif action == 'remove':
            if quantity < 0:
                quantity *= -1

            cart_product[product_color_size_pk]['quantity'] -= quantity
            messages.success(self.request, _('Remove product'))

        if cart_product[product_color_size_pk]['quantity'] <= 0:
            del cart_product[product_color_size_pk]
            messages.success(self.request, _('Delete product'))

        self.save()

    def clear_cart(self):
        """
        Clear the entire shopping cart.

        This method removes all items from the shopping cart, effectively resetting
        it to an empty state. After clearing the cart, the updated state is saved
        to reflect the changes in the user's session.
        """
        del self.session['cart']
        self.save()

    def get_total_no_discount_item(self, product_pk, item_key):
        """
        Calculate the total price for a specific item without considering discounts.

        Args:
            product_pk: The primary key of the associated product.
            item_key: The key representing the specific item in the cart.

        Returns:
            int: The total price for the item without applying any discounts.

        This method calculates the total price for a specific item in the shopping
        cart by multiplying the item's quantity with its unit price. It returns an
        integer value representing the total price without considering any discounts.
        """
        product_pk_str = str(product_pk)
        product_in_cart = self.cart[product_pk_str]
        price = product_in_cart[item_key]['price'] * product_in_cart[item_key]['quantity']
        return price

    def get_total_with_discount_item(self, product_pk, item_key):
        """
        Calculate the total price for a specific item, considering applied discounts.

        Args:
            product_pk: The primary key of the associated product.
            item_key: The key representing the specific item in the cart.

        Returns:
            int: The total price for the item after applying any applicable discounts.

        This method calculates the total price for a specific item in the shopping
        cart, taking into account any discounts applied to the unit price. It returns
        an int value representing the total price after applying discounts.
        """
        product_pk_str = str(product_pk)
        product_in_cart = self.cart[product_pk_str]
        price = 0
        if product_in_cart[item_key]['discount']:
            price = product_in_cart[item_key]['discount_price'] * product_in_cart[item_key]['quantity']
        return price

    def get_total_profit_item(self, product_pk, item_key):
        """
        Calculate the total profit for a specific item, accounting for discounts.

        Args:
            product_pk: The primary key of the associated product.
            item_key: The key representing the specific item in the cart.

        Returns:
            int: The total profit for the item, considering applied discounts.

        This method calculates the total profit for a specific item in the shopping
        cart by subtracting the discounted total price from the total price without
        discounts. It returns an int value representing the total profit after
        accounting for any applied discounts.
        """
        product_pk_str = str(product_pk)
        product_in_cart = self.cart[product_pk_str]
        price = 0
        if product_in_cart[item_key]['discount']:
            price = self.get_total_no_discount_item(product_pk, item_key) - self.get_total_with_discount_item(
                product_pk, item_key)
        return price

    def get_total_item(self, product_pk, item_key):
        """
        Calculate the net total price for a specific item, factoring in profit.

        Args:
            product_pk: The primary key of the associated product.
            item_key: The key representing the specific item in the cart.

        Returns:
            int: The net total price for the item after accounting for profit.

        This method calculates the net total price for a specific item in the shopping
        cart by subtracting the total profit from the total price without discounts.
        It returns an int value representing the net total price, considering profit.
        """
        return self.get_total_no_discount_item(product_pk, item_key) - self.get_total_profit_item(product_pk, item_key)
