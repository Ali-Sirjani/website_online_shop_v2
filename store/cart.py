import math

from django.contrib import messages
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404

from .models import Product, ProductColorAndSizeValue, Coupon


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

    def __iter__(self, clac_price=False):
        """
        Iterate through the items in the shopping cart.

        This iterator method fetches information about each product in the cart,
        including color and size details if applicable. It yields dictionaries
        containing relevant information for each item. The dictionaries are keyed
        using a numeric flag variable starting from 1.

        Example of yielded item:
        {
            '1': {
                'product': Product instance,  # The product associated with the item.
                'color_size': ColorSize instance or None,  # Color and size information if applicable.
                'quantity': 2,  # The quantity of the product in the cart.
                'price': 29.99,  # The unit price of the product.
                'discount': 0.15,  # The discount percentage, if any.
                'discount_price': 25.49,  # The discounted price after applying discounts.
                'get_total_no_discount_item': 50.98,  # Total price without discounts for the item.
                'get_total_with_discount_item': 42.98,  # Total price with discounts for the item.
                'get_total_profit_item': 8.0,  # Total profit from the item.
                'get_total_item': 42.98  # Total price after accounting for profit.
            }
        }
        """
        color_size_pks = {}
        products_pk = []
        for product_key in self.cart.keys():
            products_pk.append(product_key[0])
            color_size_pks[product_key] = []
            for item in self.cart[product_key].keys():
                color_size_pks[product_key].append(item)

        items = {}
        flag = 1

        if products_pk:
            if clac_price:
                for product_key in products_pk:
                    for item_key in self.cart[product_key]:
                        flag_str = str(flag)
                        items[flag_str] = {}
                        items[flag_str]['get_total_no_discount_item'] = self.get_total_no_discount_item(product_key,
                                                                                                        item_key)
                        items[flag_str]['get_total_with_discount_item'] = self.get_total_with_discount_item(product_key,
                                                                                                            item_key)
                        items[flag_str]['get_total_profit_item'] = self.get_total_profit_item(product_key, item_key)
                        items[flag_str]['get_total_item'] = self.get_total_item(product_key, item_key)

                        flag += 1

            else:
                cart_products = Product.objects.filter(pk__in=products_pk).prefetch_related('images')
                for product in cart_products:
                    product_pk_str = str(product.pk)
                    product_color_size_queryset = product.color_size_values.all().select_related('color', 'size')
                    for item_key in color_size_pks[product_pk_str]:
                        flag_str = str(flag)
                        items[flag_str] = {}

                        items[flag_str]['product'] = product
                        if item_key != 'None':
                            items[flag_str]['color_size'] = product_color_size_queryset.get(pk=item_key)
                        items[flag_str]['quantity'] = self.cart[product_pk_str][item_key]['quantity']
                        items[flag_str]['price'] = self.cart[product_pk_str][item_key]['price']
                        items[flag_str]['discount'] = self.cart[product_pk_str][item_key]['discount']
                        items[flag_str]['discount_price'] = self.cart[product_pk_str][item_key]['discount_price']
                        items[flag_str]['get_total_no_discount_item'] = self.get_total_no_discount_item(product_pk_str,
                                                                                                        item_key)
                        items[flag_str]['get_total_with_discount_item'] = self.get_total_with_discount_item(
                            product_pk_str,
                            item_key)
                        items[flag_str]['get_total_profit_item'] = self.get_total_profit_item(product_pk_str, item_key)
                        items[flag_str]['get_total_item'] = self.get_total_item(product_pk_str, item_key)

                        flag += 1

        for item in items.values():
            yield item

    def save(self):
        """
        Save the current state of the shopping cart.

        This method marks the user's session as modified, indicating that changes
        have been made to the shopping cart. This ensures that the updated cart
        information is persisted between requests.
        """
        self.session.modified = True

    def act_items(self):
        """
        Retrieve active items from the shopping cart.

        This method returns an iterator of dictionaries containing information
        about each active item in the shopping cart. The structure of the yielded
        items is designed to align with the usage in templates, mirroring the Order
        model's structure for seamless integration and consistency.

        The method name 'act_items' is chosen to resemble the terminology used in
        the Order model, ensuring a consistent and intuitive interface for template
        usage.
        :return: self.__iter__()
        """
        try:
            first = next(self.__iter__())
        except StopIteration:
            return None

        return self.__iter__()

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
            cart_product[product_color_size_pk] = {'quantity': 0}
            self.set_price_item(cart_product[product_color_size_pk], product_pk_str, product_color_size_pk)

        if cart_product[product_color_size_pk]['quantity'] * -1 > quantity or action == 'delete_item':
            del cart_product[product_color_size_pk]
            messages.success(self.request, _('Delete product'))
            self.save()
            return

        elif action == 'add':
            cart_product[product_color_size_pk]['quantity'] += quantity
            messages.success(self.request, _('Add product'))

        elif action == 'replace':
            cart_product[product_color_size_pk]['quantity'] = quantity
            messages.success(self.request, _('Cart update'))

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

    @property
    def get_cart_items(self):
        """
        Retrieve the total quantity of items in the shopping cart.

        Returns:
            int: The total quantity of items in the cart.

        This method returns the total quantity of items in the shopping cart,
        summing up the quantities of all active items.
        """
        quantity = 0
        for product_key in self.cart.keys():
            for item in self.cart[product_key].values():
                quantity += item['quantity']
        return quantity

    @property
    def get_cart_total_no_discount(self):
        """
        Calculate the total price of items in the shopping cart without considering discounts.

        Returns:
            int: The total price of all items in the cart without applying any discounts.

        This method calculates the total price of all items in the shopping cart by
        summing up the individual total prices of each item, without considering any discounts.
        """
        total_no_discount = 0
        for item in self.__iter__(True):
            total_no_discount += item['get_total_no_discount_item']
        return total_no_discount

    @property
    def get_cart_total_profit(self):
        """
        Calculate the total profit from items in the shopping cart, accounting for discounts.

        Returns:
            int: The total profit from all items in the cart, considering applied discounts.

        This method calculates the total profit from all items in the shopping cart by
        summing up the individual total profits of each item, accounting for any discounts.
        """
        total_profit = 0
        for item in self.__iter__(True):
            total_profit += item['get_total_profit_item']
        return total_profit

    @property
    def get_cart_total(self):
        """
        Calculate the net total price of items in the shopping cart, factoring in profit.

        Returns:
            int: The net total price of all items in the cart after accounting for profit.

        This method calculates the net total price of all items in the shopping cart by
        subtracting the total profit from the total price without discounts.
        """
        cart_total = 0
        for item in self.__iter__(True):
            cart_total += item['get_total_item']
        return cart_total

    def calculate_coupon_price(self, success_message=True):
        coupon_pk = self.coupon.get('coupon_pk')

        if coupon_pk:
            coupon_obj = get_object_or_404(Coupon, pk=coupon_pk)
            if coupon_obj and coupon_obj.can_use():
                coupon_rules = coupon_obj.rules.all().order_by('-start_price')
                for coupon_rule in coupon_rules:
                    new_cart_total = coupon_rule.apply_discount(self.get_cart_total)
                    if new_cart_total:
                        self.coupon['coupon_price'] = math.ceil(new_cart_total)
                        self.save()
                        if success_message:
                            messages.success(self.request,
                                             _('Congratulations! 🎉 Your coupon has been successfully applied. Thank you for choosing us! Happy shopping!')
                                             )
                        return True

                messages.info(self.request, _(f'The minimum price for coupon is {coupon_rules.last().start_price}'))

            else:
                messages.error(self.request, _(f'The {coupon_obj} is not valid'))

            self.coupon['coupon_pk'] = None
            self.coupon['coupon_price'] = 0
            self.save()

        return False

    @property
    def coupon_price(self):
        return self.coupon.get('coupon_price')

    @property
    def get_cart_total_with_coupon(self):
        coupon_price = self.coupon.get('coupon_price')
        if self.coupon.get('coupon_pk') and coupon_price:
            return (self.get_cart_total_no_discount - self.get_cart_total_profit) - self.coupon_price

        return 0
