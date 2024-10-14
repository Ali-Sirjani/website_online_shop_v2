import json

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from ..models import Product, ProductColor, ProductSize, ProductColorAndSizeValue, Order, OrderItem, Coupon, CouponRule


class UpdateItemViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user
        cls.user = get_user_model().objects.create_user(username='testuser', password='testpassword')

        # Create test data (adjust as needed)
        # Product 1
        cls.product1 = Product.objects.create(title='Test Product 1', price=10, discount=False, inventory=10)
        # Product 2
        cls.product2 = Product.objects.create(title='Test Product 2', price=20, discount=True, discount_price=14,
                                              inventory=5)
        # Product 3
        cls.product3 = Product.objects.create(title='Test Product 3', price=15, discount=False, inventory=8)
        # Product 4
        cls.product4 = Product.objects.create(title='Test Product 4', price=15, discount=False, inventory=0)
        # Color 1
        cls.color1 = ProductColor.objects.create(name='Red', color='#FF0000')
        # Color 2
        cls.color2 = ProductColor.objects.create(name='Blue', color='#0000FF')
        # Size 1
        cls.size1 = ProductSize.objects.create(size='Small')
        # Size 2
        cls.size2 = ProductSize.objects.create(size='Large')
        # Color Size Value 1
        cls.color_size_value1 = ProductColorAndSizeValue.objects.create(
            product=cls.product1, color=cls.color1, size=cls.size1, additional_cost=5, inventory=8, is_active=True
        )
        # Color Size Value 2
        cls.color_size_value2 = ProductColorAndSizeValue.objects.create(
            product=cls.product1, color=cls.color2, size=cls.size1, additional_cost=3, inventory=10, is_active=True
        )
        # Color Size Value 3
        cls.color_size_value3 = ProductColorAndSizeValue.objects.create(
            product=cls.product2, color=cls.color2, size=cls.size2, additional_cost=10, inventory=3, is_active=True
        )

    def send_request_authenticated_user(self, data, status_code_expected):
        response = self.client.post(reverse('store:update_item'), data=json.dumps(data),
                                    content_type='application/json')

        # Check the response status
        self.assertEqual(response.status_code, status_code_expected)

    def send_request_unauthenticated_user(self, data, status_code_expected):
        response = self.client.post(reverse('store:update_item'), data=json.dumps(data),
                                    content_type='application/json')

        # Check the response status
        self.assertEqual(response.status_code, status_code_expected)

        # Check that the cart data is stored in the session
        return self.client.session.get('cart')

    def test_update_item_authenticated_user_actions_add_replace_remove(self):
        # Log in the user
        self.client.force_login(self.user)

        # Simulate an update item request action add
        data = {
            'quantity': 3,
            'productId': self.product1.pk,
            'colorId': self.color1.pk,
            'sizeId': self.size1.pk,
            'colorSizeId': self.color_size_value1.pk,
            'action': 'add',
        }

        self.send_request_authenticated_user(data, 200)

        # Check that the order item was created and has the correct quantity
        order = Order.objects.get(customer=self.user, completed=False)
        order_item = OrderItem.objects.get(order=order, product=self.product1, color_size=self.color_size_value1)
        self.assertEqual(order_item.quantity, 3)

        # Simulate an update item request without color size value, action remove(quantity less than itme.quantity)
        data = {
            'quantity': -2,
            'productId': self.product1.pk,
            'colorId': self.color1.pk,
            'sizeId': self.size1.pk,
            'action': 'remove',
        }
        self.send_request_authenticated_user(data, 200)

        # Check that the order item was created and has the correct quantity
        order_item.refresh_from_db()
        self.assertEqual(order_item.quantity, 1)

        # Simulate an update item request without color and size, action replace
        data = {
            'quantity': 4,
            'productId': self.product1.pk,
            'colorSizeId': self.color_size_value1.pk,
            'action': 'replace',
        }
        self.send_request_authenticated_user(data, 200)

        # Check that the order item was created and has the correct quantity
        order_item.refresh_from_db()
        self.assertEqual(order_item.quantity, 4)

        # Simulate an update item request without color size value, action remove(quantity equal to item.quantity)
        data = {
            'quantity': -4,
            'productId': self.product1.pk,
            'colorId': self.color1.pk,
            'sizeId': self.size1.pk,
            'action': 'remove',
        }
        self.send_request_authenticated_user(data, 200)

        with self.assertRaises(OrderItem.DoesNotExist):
            OrderItem.objects.get(order=order, product=self.product1, color_size=self.color_size_value1)

    def test_update_item_authenticated_user_actions_delete_item_and_delete_cart(self):
        # Log in the user
        self.client.force_login(self.user)

        # test delete item action
        # Simulate an update item request action add
        data = {
            'quantity': 2,
            'productId': self.product1.pk,
            'colorSizeId': self.color_size_value2.pk,
            'action': 'add',
        }
        self.send_request_authenticated_user(data, 200)

        # Simulate an update item request action add
        data = {
            'quantity': 3,
            'productId': self.product2.pk,
            'colorSizeId': self.color_size_value3.pk,
            'action': 'add',
        }
        self.send_request_authenticated_user(data, 200)

        order = Order.objects.get(customer=self.user, completed=False)
        self.assertEqual(len(order.items.all()), 2)
        order_item1 = OrderItem.objects.get(order=order, product=self.product2, color_size=self.color_size_value3.pk)

        # Simulate an update item request action delete_item
        data['action'] = 'delete_item'
        self.send_request_authenticated_user(data, 200)
        self.assertEqual(len(order.items.all()), 1)

        with self.assertRaises(OrderItem.DoesNotExist):
            OrderItem.objects.get(pk=order_item1.pk)

        # test delete cart action
        # Simulate an update item request action add with none color size value
        data = {
            'quantity': 3,
            'productId': self.product3.pk,
            'action': 'add',
        }
        self.send_request_authenticated_user(data, 200)

        OrderItem.objects.get(order=order, product=self.product3, color_size=None)

        # Simulate an update item request action add
        data = {
            'quantity': 2,
            'productId': self.product1.pk,
            'colorSizeId': self.color_size_value1.pk,
            'action': 'add',
        }
        self.send_request_authenticated_user(data, 200)

        OrderItem.objects.get(order=order, product=self.product1, color_size=self.color_size_value1)

        # this order item was created
        OrderItem.objects.get(order=order, product=self.product1, color_size=self.color_size_value2)

        self.assertEqual(len(order.items.all()), 3)
        # Simulate an update item request action delete_item
        data['action'] = 'delete_cart'
        self.send_request_authenticated_user(data, 200)

        self.assertEqual(len(order.items.all()), 0)

    def test_update_item_authenticated_user_with_invalid_data(self):
        # Log in the user
        self.client.force_login(self.user)

        # Simulate an update item request action add for inactive product
        data = {
            'quantity': 3,
            'productId': self.product4.pk,
            'action': 'add',
        }
        self.send_request_authenticated_user(data, 404)

        # Simulate an update item request action add with invalid color size value for product1
        data = {
            'quantity': 3,
            'productId': self.product1.pk,
            'colorSizeId': self.color_size_value3.pk,
            'action': 'add',
        }
        self.send_request_authenticated_user(data, 400)

        # Simulate an update item request action add with invalid color size value for product1
        data = {
            'quantity': 3,
            'productId': self.product2.pk,
            'colorId': self.color1.pk,
            'sizeId': self.size1.pk,
            'action': 'add',
        }
        self.send_request_authenticated_user(data, 400)

        # Simulate an update item request action replace with invalid color size value for product1
        data = {
            'quantity': 3,
            'productId': self.product2.pk,
            'colorId': self.color1.pk,
            'sizeId': self.size1.pk,
            'action': 'replace',
        }
        self.send_request_authenticated_user(data, 400)

        # Simulate an update item request action remove with product1 that is not added
        data = {
            'quantity': -3,
            'productId': self.product1.pk,
            'colorId': self.color1.pk,
            'sizeId': self.size1.pk,
            'action': 'remove',
        }
        self.send_request_authenticated_user(data, 400)

        # Simulate an update item request action delete item with product1 that is not added
        data = {
            'quantity': 3,
            'productId': self.product2.pk,
            'colorSizeId': self.color_size_value3.pk,
            'action': 'delete_item',
        }
        self.send_request_authenticated_user(data, 400)

    def test_update_item_unauthenticated_user_actions_add_replace_remove(self):
        # Simulate an update item request (add to cart) for an unauthenticated user with color size value
        data = {
            'quantity': 2,
            'productId': self.product1.pk,
            'colorId': self.color1.pk,
            'sizeId': self.size1.pk,
            'colorSizeId': self.color_size_value1.pk,
            'action': 'add',
        }

        # Check that the cart data is stored in the session
        session_cart = self.send_request_unauthenticated_user(data, 200)
        self.assertIsNotNone(session_cart)

        # checks cart structure
        product_pk_str = str(self.product1.pk)
        color_size_value_str = str(self.color_size_value1.pk)
        self.assertIn(product_pk_str, session_cart.keys())
        self.assertIn(color_size_value_str, session_cart[product_pk_str].keys())
        self.assertEqual(session_cart.get(product_pk_str, {}).get(color_size_value_str, {}).get('quantity'), 2)

        # Simulate an update item request (add to cart) for an unauthenticated user without color size value
        data = {
            'quantity': 5,
            'productId': self.product3.pk,
            'action': 'add',
        }
        session_cart = self.send_request_unauthenticated_user(data, 200)

        # checks cart structure
        product_pk_str = str(self.product3.pk)
        self.assertIn(product_pk_str, session_cart.keys())
        self.assertIn('None', session_cart[product_pk_str].keys())
        self.assertEqual(session_cart.get(product_pk_str, {}).get('None', {}).get('quantity'), 5)

        # Simulate an update item request (replace) for an unauthenticated user
        data = {
            'quantity': 7,
            'productId': self.product1.pk,
            'colorSizeId': self.color_size_value1.pk,
            'action': 'replace',
        }

        # Check that the cart data is stored in the session
        session_cart = self.send_request_unauthenticated_user(data, 200)

        # checks cart structure
        product_pk_str = str(self.product1.pk)
        color_size_value_str = str(self.color_size_value1.pk)
        self.assertEqual(session_cart.get(product_pk_str, {}).get(color_size_value_str, {}).get('quantity'), 7)

        # Simulate an update item request (remove item, quantity less than item quantity)
        # for an unauthenticated user with color size value
        data = {
            'quantity': 1,
            'productId': self.product1.pk,
            'colorSizeId': self.color_size_value1.pk,
            'action': 'remove',
        }
        session_cart = self.send_request_unauthenticated_user(data, 200)

        # checks cart structure
        product_pk_str = str(self.product1.pk)
        color_size_value_str = str(self.color_size_value1.pk)
        self.assertEqual(session_cart.get(product_pk_str, {}).get(color_size_value_str, {}).get('quantity'), 6)

        # Simulate an update item request (remove item, quantity less than item quantity)
        # for an unauthenticated user without color size value
        data = {
            'quantity': -3,
            'productId': self.product3.pk,
            'action': 'remove',
        }

        session_cart = self.send_request_unauthenticated_user(data, 200)

        self.assertEqual(session_cart.get(str(self.product3.pk), {}).get('None', {}).get('quantity'), 2)

        # Simulate an update item request (remove item, quantity more than item quantity)
        # for an unauthenticated user with color size value
        data = {
            'quantity': 10,
            'productId': self.product1.pk,
            'colorSizeId': self.color_size_value1.pk,
            'action': 'remove',
        }
        session_cart = self.send_request_unauthenticated_user(data, 200)

        # checks cart structure
        product_pk_str = str(self.product1.pk)
        self.assertEqual(session_cart.get(product_pk_str), {})

        # Simulate an update item request (remove item, quantity less than item quantity)
        # for an unauthenticated user without color size value
        data = {
            'quantity': -2,
            'productId': self.product3.pk,
            'action': 'remove',
        }
        session_cart = self.send_request_unauthenticated_user(data, 200)

        product_pk_str = str(self.product1.pk)
        self.assertEqual(session_cart.get(product_pk_str), {})

    def test_update_item_unauthenticated_user_actions_delete_item_and_delete_cart(self):
        data = {
            'quantity': 2,
            'productId': self.product1.pk,
            'colorSizeId': self.color_size_value1.pk,
            'action': 'add',
        }
        self.send_request_unauthenticated_user(data, 200)

        data = {
            'quantity': 5,
            'productId': self.product1.pk,
            'colorSizeId': self.color_size_value2.pk,
            'action': 'add',
        }
        self.send_request_unauthenticated_user(data, 200)

        data = {
            'quantity': 3,
            'productId': self.product2.pk,
            'colorSizeId': self.color_size_value3.pk,
            'action': 'add',
        }
        self.send_request_unauthenticated_user(data, 200)

        data = {
            'quantity': 1,
            'productId': self.product3.pk,
            'action': 'add',
        }
        section_cart = self.send_request_unauthenticated_user(data, 200)

        self.assertEqual(len(section_cart.keys()), 3)
        self.assertEqual(len(section_cart[str(self.product1.pk)].keys()), 2)
        self.assertEqual(len(section_cart[str(self.product2.pk)].keys()), 1)
        self.assertEqual(len(section_cart[str(self.product3.pk)].keys()), 1)

        data = {
            'quantity': 1,
            'productId': self.product2.pk,
            'colorSizeId': self.color_size_value3.pk,
            'action': 'delete_item',
        }
        section_cart = self.send_request_unauthenticated_user(data, 200)
        self.assertEqual(section_cart.get(str(self.product2.pk)), {})

        data = {
            'quantity': 1,
            'action': 'delete_cart',
        }
        section_cart = self.send_request_unauthenticated_user(data, 200)
        self.assertIsNone(section_cart)

    def test_update_item_unauthenticated_user_with_invalid_data(self):
        # Simulate an update item request (add to cart) for an unauthenticated user with inactive product
        data = {
            'quantity': 2,
            'productId': self.product4.pk,
            'action': 'add',
        }

        # Check that the cart data is stored in the session
        self.send_request_unauthenticated_user(data, 404)

        # Simulate an update item request (add to cart) for an unauthenticated user with invalid color size value
        data = {
            'quantity': 2,
            'productId': self.product1.pk,
            'colorSizeId': self.color_size_value3.pk,
            'action': 'add',
        }
        # Check that the cart data is stored in the session
        self.send_request_unauthenticated_user(data, 400)

        # Simulate an update item request (add to cart) for an unauthenticated user with invalid color and size
        data = {
            'quantity': 2,
            'productId': self.product2.pk,
            'colorId': self.color2.pk + 10,
            'sizeId': self.size2.pk + 10,
            'action': 'add',
        }

        # Check that the cart data is stored in the session
        self.send_request_unauthenticated_user(data, 404)

        # Simulate an update item request (add to cart) for an unauthenticated user
        # with invalid color and size for product2
        data = {
            'quantity': 2,
            'productId': self.product2.pk,
            'colorId': self.color1.pk,
            'sizeId': self.size1.pk,
            'action': 'add',
        }

        # Check that the cart data is stored in the session
        self.send_request_unauthenticated_user(data, 400)

        # Simulate an update item request (add to cart) for an unauthenticated user
        # with invalid color and size for product2
        data = {
            'quantity': -2,
            'productId': self.product2.pk,
            'colorId': self.color2.pk,
            'sizeId': self.size2.pk,
            'action': 'remove',
        }

        # Check that the cart data is stored in the session
        self.send_request_unauthenticated_user(data, 400)


class CartViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')

        # Create test data (adjust as needed)
        self.product = Product.objects.create(title='Test Product', price=10, discount=False, inventory=10)
        self.color = ProductColor.objects.create(name='Red', color='#FF0000')
        self.size = ProductSize.objects.create(size='Small')
        self.color_size_value = ProductColorAndSizeValue.objects.create(
            product=self.product, color=self.color, size=self.size, additional_cost=0, inventory=10, is_active=True
        )

    def add_to_cart(self):
        data = {
            'quantity': 2,
            'productId': self.product.pk,
            'colorSizeId': self.color_size_value.pk,
            'action': 'add',
        }

        response = self.client.post(reverse('store:update_item'), data=json.dumps(data),
                                    content_type='application/json')

        # Check the response status
        self.assertEqual(response.status_code, 200)

    def test_cart_view_authenticated_user(self):
        # Log in the user
        self.client.force_login(self.user)
        self.add_to_cart()

        # Access the cart view
        response = self.client.get(reverse('store:cart_page'))

        # Check that the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that templated used
        self.assertTemplateUsed(response, 'store/order/cart.html')

        # Check that the expected context data is present
        self.assertIn('order', response.context)

        # product data
        order = response.context['order']
        order_items = order.items.all()
        self.assertEqual(len(order_items), 1)
        self.assertEqual(self.product, order_items.first().product)

    def test_cart_view_unauthenticated_user(self):
        # Access the cart view as an unauthenticated user
        self.add_to_cart()
        response = self.client.get(reverse('store:cart_page'))

        # Check that the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that templated used
        self.assertTemplateUsed(response, 'store/order/cart.html')

        # Check that the expected context data is present
        self.assertIn('cart', self.client.session)
        self.assertIn('order', response.context)

        # product data
        order = response.context['order']
        order_items = order.act_items()
        order_item_list = []
        for order_item in order_items:
            order_item_list.append(order_item['product'])

        self.assertEqual(len(order_item_list), 1)
        self.assertEqual(self.product, order_item_list[0])


class ApplyCouponViewTest(TestCase):
    def setUp(self):
        # create user
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword', )
        # create order
        self.order = Order.objects.create(customer=self.user, completed=False, )

        # Product 1
        self.product1 = Product.objects.create(title='Test Product 1', price=10, discount=False, inventory=10,
                                               is_active=True, )
        # Product 2
        self.product2 = Product.objects.create(title='Test Product 2', price=20, discount=True, discount_price=14,
                                               inventory=5, is_active=True, )

        # create order item
        self.order_item1 = OrderItem.objects.create(product=self.product1, order=self.order, quantity=1)
        self.order_item2 = OrderItem.objects.create(product=self.product2, order=self.order, quantity=2)

        # create coupon
        self.coupon = Coupon.objects.create(
            code='TESTCODE',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=7),
            num_available=10,
            num_used=0,
            reason_make='Test coupon',
            is_active=True,
        )
        # create coupon rule
        self.rule1 = CouponRule.objects.create(
            coupon=self.coupon,
            discount_percentage=10,
            start_price=50,
        )
        self.rule2 = CouponRule.objects.create(
            coupon=self.coupon,
            discount_percentage=15,
            start_price=100,
        )
        self.rule3 = CouponRule.objects.create(
            coupon=self.coupon,
            discount_percentage=30,
            start_price=500,
        )

    def reqeust_apply_coupon(self, coupon_code='TESTCODE'):
        data = {'code': coupon_code}
        response = self.client.post(reverse('store:apply_coupon'), data=data, HTTP_REFERER=reverse('core:home_page'))
        return response

    def add_item_user_unauthenticated(self):
        """
        cart item structure:
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
        session = self.client.session
        session['cart'] = {
            str(self.product1.pk): {
                'None': {'quantity': 3, 'price': self.product1.price, 'discount': self.product1.discount,
                         'discount_price': self.product1.discount_price}},
            str(self.product2.pk): {
                'None': {'quantity': 1, 'price': self.product2.price, 'discount': self.product2.discount,
                         'discount_price': self.product2.discount_price}},
        }
        session.save()

    def test_apply_valid_coupon_authenticated_user(self):
        self.client.force_login(self.user)
        # send request with total 38, the smallest start_price is 50
        response = self.reqeust_apply_coupon()
        self.assertEqual(response.status_code, 302)
        # Check that the coupon is not applied to the order
        self.order.refresh_from_db()
        self.assertEqual(self.order.coupon, None)

        # increase total price
        self.order_item1.price = 22
        self.order_item1.save()

        # send request with total 50, the smallest start_price is 50
        response = self.reqeust_apply_coupon()
        self.assertEqual(response.status_code, 302)
        # Check that the coupon is not applied to the order
        self.order.refresh_from_db()
        self.assertEqual(self.order.coupon, self.coupon)
        self.assertEqual(self.order.coupon_price, 5)
        self.assertEqual(self.order.get_cart_total, 50)
        self.assertEqual(self.order.get_cart_total_with_coupon, 45)

        # increase total price
        self.order_item1.price = 522
        self.order_item1.save()

        # send request with total 550, the biggest start_price is 500
        response = self.reqeust_apply_coupon()
        self.assertEqual(response.status_code, 302)
        # Check that the coupon is not applied to the order
        self.order.refresh_from_db()
        self.assertEqual(self.order.coupon, self.coupon)
        self.assertEqual(self.order.coupon_price, 165)
        self.assertEqual(self.order.get_cart_total, 550)
        self.assertEqual(self.order.get_cart_total_with_coupon, 385)

    def test_apply_invalid_coupon_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.reqeust_apply_coupon('WrongCode')

        self.assertIsNone(self.order.coupon)
        self.assertEqual(self.order.coupon_price, 0)

    def test_apply_valid_coupon_unauthenticated_user(self):
        self.add_item_user_unauthenticated()
        # send request with total 44, the smallest start_price is 50
        response = self.reqeust_apply_coupon()
        self.assertEqual(response.status_code, 302)
        # Check that the coupon is not applied to the order
        self.assertEqual(self.client.session['coupon']['coupon_pk'], None)

        # increase total price
        session = self.client.session
        session['cart'][str(self.product1.pk)]['None']['price'] = 50
        session.save()

        # send request with total 164, the start_price is 100
        response = self.reqeust_apply_coupon()
        self.assertEqual(response.status_code, 302)
        # Check that the coupon is not applied to the order
        response_include_order = self.client.get(reverse('core:home_page'))
        order = response_include_order.context['order']
        coupon = self.client.session['coupon']
        self.assertEqual(coupon['coupon_pk'], self.coupon.pk)
        self.assertEqual(coupon['coupon_price'], 25)
        self.assertEqual(order.get_cart_total, 164)
        self.assertEqual(order.get_cart_total_with_coupon, 139)

        # increase total price
        session = self.client.session
        session['cart'][str(self.product1.pk)]['None']['price'] = 200
        session.save()

        # send request with total 614, the biggest start_price is 500
        response = self.reqeust_apply_coupon()
        self.assertEqual(response.status_code, 302)
        # Check that the coupon is not applied to the order
        response_include_order = self.client.get(reverse('core:home_page'))
        order = response_include_order.context['order']
        coupon = self.client.session['coupon']
        self.assertEqual(coupon['coupon_pk'], self.coupon.pk)
        self.assertEqual(coupon['coupon_price'], 185)
        self.assertEqual(order.get_cart_total, 614)
        self.assertEqual(order.get_cart_total_with_coupon, 429)

    def test_apply_invalid_coupon_unauthenticated_user(self):
        self.add_item_user_unauthenticated()

        # When coupon is invalid Cart object not will create
        response = self.reqeust_apply_coupon('WrongCode')

        self.assertIsNone(self.client.session.get('coupon'))


class OrderDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create two test users
        cls.user1 = get_user_model().objects.create_user(username='testuser1', password='testpassword1')
        cls.user2 = get_user_model().objects.create_user(username='testuser2', password='testpassword2',
                                                         email='Test@gmail.com')

        # Create a test order completed for user 1
        cls.order1 = Order.objects.create(customer=cls.user1, completed=True)
        # Create a test order incomplete for user 1
        cls.order2 = Order.objects.create(customer=cls.user1, completed=False)

        # Create a test order for user 2
        cls.order3 = Order.objects.create(customer=cls.user2, completed=True)

    def test_template_used(self):
        # Log in the user
        self.client.force_login(self.user1)

        # Access the order detail view
        response = self.client.get(reverse('store:order_detail', args=[self.order1.pk]))

        # Check that the response status is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check that the correct template is used
        self.assertTemplateUsed(response, 'store/order/order_detail.html')

    def test_unauthenticated_user(self):
        response = self.client.get(reverse('store:order_detail', args=[self.order1.pk]))

        self.assertEqual(response.status_code, 302)

    def test_access_user_to_order_detail(self):
        # Log in the user2
        self.client.force_login(self.user2)

        # order1 is for user1
        response = self.client.get(reverse('store:order_detail', args=[self.order1.pk]))

        self.assertEqual(response.status_code, 404)

    def test_incomplete_order(self):
        # Log in the user1
        self.client.force_login(self.user1)

        # order2 is incomplete
        response = self.client.get(reverse('store:order_detail', args=[self.order2.pk]))

        self.assertEqual(response.status_code, 404)
