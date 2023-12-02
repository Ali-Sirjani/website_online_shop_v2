from django.db.models import Q

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
