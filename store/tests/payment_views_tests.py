from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from ..models import Order, OrderItem, Product


class CheckoutViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up a sample order for testing
        # create user
        cls.user1 = get_user_model().objects.create_user(username='testuser1', password='testpassword1')
        cls.user2 = get_user_model().objects.create_user(username='testuser2', password='testpassword2',
                                                         email='Test@gmail.com')

        # create order
        cls.order1 = Order.objects.create(
            customer=cls.user1,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='+1234567890',
            order_note='Test Order',
            completed=False,
        )
        cls.order2 = Order.objects.create(
            customer=cls.user2,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='+1234567890',
            order_note='Test Order',
            completed=False,
        )

        # create product
        cls.product1 = Product.objects.create(title='Product 1', short_description='short description for product 1',
                                              price=100, inventory=10, discount=True, discount_price=70, is_active=True)
        cls.product2 = Product.objects.create(title='Product 2', short_description='short description for product 2',
                                              price=150, inventory=15, is_active=True)

        # create order item
        cls.order_item1 = OrderItem.objects.create(
            product=cls.product1,
            order=cls.order1,
            quantity=2,
        )
        cls.order_item2 = OrderItem.objects.create(
            product=cls.product2,
            order=cls.order1,
            quantity=3,
        )

    def test_empty_cart(self):
        # unauthenticated user
        response = self.client.get(reverse('store:checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('store:product_list'))

        # authenticated user
        self.client.force_login(self.user2)

        response = self.client.get(reverse('store:checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('store:product_list'))

    def test_template(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('store:checkout'))
        self.assertTemplateUsed(response, 'store/payment/checkout.html')
