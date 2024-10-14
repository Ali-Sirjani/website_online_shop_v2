from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from ..models import Coupon, generate_coupon_code, CouponRule, Order, OrderItem, ShippingAddress
from .product_views_tests import create_product_test_data


class CouponModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up a sample coupon for testing
        cls.sample_coupon = Coupon.objects.create(
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=7),
            num_available=10,
            num_used=5,
            reason_make="Test Coupon",
            is_active=True
        )

    def test_coupon_model_attributes(self):
        # Test all data attributes of the Coupon model
        self.assertIsNotNone(self.sample_coupon.code)
        self.assertIsNotNone(self.sample_coupon.start_date)
        self.assertIsNotNone(self.sample_coupon.end_date)
        self.assertEqual(self.sample_coupon.num_available, 10)
        self.assertEqual(self.sample_coupon.num_used, 5)
        self.assertEqual(self.sample_coupon.reason_make, "Test Coupon")
        self.assertTrue(self.sample_coupon.is_active)

        # Check if datetime_created and datetime_updated are not None
        self.assertIsNotNone(self.sample_coupon.datetime_created)
        self.assertIsNotNone(self.sample_coupon.datetime_updated)

        # Test string representation
        self.assertEqual(str(self.sample_coupon), self.sample_coupon.code)

    def test_unique_code_constraint(self):
        # create a coupon object
        Coupon.objects.create(
            code='code is for test',
            num_available=10,
            num_used=5,
            reason_make="Test Coupon",
            is_active=True
        )

        with self.assertRaises(IntegrityError):
            # create a coupon object with same code
            Coupon.objects.create(
                code='code is for test',
                num_available=10,
                num_used=5,
                reason_make="Test Coupon",
                is_active=True
            )

    def test_can_use_method(self):
        # Test the can_use method of the Coupon model.
        # Assuming the sample coupon is set to be active
        self.assertTrue(self.sample_coupon.can_use())

        # Deactivate the coupon and check if it can't be used
        self.sample_coupon.is_active = False
        self.assertFalse(self.sample_coupon.can_use())

        # Expire the coupon and check if it can't be used and set is_active True again
        self.sample_coupon.is_active = True
        self.sample_coupon.end_date = timezone.now() - timezone.timedelta(days=1)
        self.assertFalse(self.sample_coupon.can_use())

        # Use up all available coupons and check if it can't be used and increase end_date
        self.sample_coupon.end_date = timezone.now() + timezone.timedelta(days=1)
        self.sample_coupon.num_used = self.sample_coupon.num_available
        self.assertFalse(self.sample_coupon.can_use())

    def test_generate_coupon_code(self):
        # Test the generate_coupon_code function.
        # Test if the generated code has the correct length
        generated_code = generate_coupon_code(length=12)
        self.assertEqual(len(generated_code), 12)

        # Test if the generated code is uppercase
        self.assertEqual(generated_code, generated_code.upper())

        # Test if the generated code is different each time
        new_generated_code = generate_coupon_code(length=12)
        self.assertNotEqual(generated_code, new_generated_code)


class CouponRuleModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up a sample coupon for testing
        cls.sample_coupon = Coupon.objects.create(
            code='TESTCODE',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=7),
            num_available=10,
            num_used=5,
            reason_make="Test Coupon",
            is_active=True
        )

        # Set up three sample rules for testing
        cls.sample_rule1 = CouponRule.objects.create(
            coupon=cls.sample_coupon,
            discount_percentage=10,
            start_price=50
        )

        cls.sample_rule2 = CouponRule.objects.create(
            coupon=cls.sample_coupon,
            discount_percentage=15,
            start_price=75
        )

        cls.sample_rule3 = CouponRule.objects.create(
            coupon=cls.sample_coupon,
            discount_percentage=20,
            start_price=100
        )

    def test_rule_model_attributes(self):
        # Test all data attributes of the CouponRule model
        self.assertEqual(self.sample_rule1.coupon, self.sample_coupon)
        self.assertEqual(self.sample_rule1.discount_percentage, 10)
        self.assertEqual(self.sample_rule1.start_price, 50)

    def test_apply_discount_method(self):
        # Test the apply_discount method of the CouponRule model
        # Test with an order total less than the start_price for rule1
        order_total_rule1 = 40
        self.assertEqual(self.sample_rule1.apply_discount(order_total_rule1), 0)

        # Test with an order total equal to the start_price for rule1
        order_total_rule1 = 50
        expected_discount_rule1 = (10 / 100) * order_total_rule1
        self.assertEqual(self.sample_rule1.apply_discount(order_total_rule1), expected_discount_rule1)

        # Test with an order total greater than the start_price for rule1 but less than rule2
        order_total_rule1 = 60
        expected_discount_rule1 = (10 / 100) * order_total_rule1
        self.assertEqual(self.sample_rule1.apply_discount(order_total_rule1), expected_discount_rule1)

        # Test with an order total less than the start_price for rule2
        order_total_rule2 = 70
        self.assertEqual(self.sample_rule2.apply_discount(order_total_rule2), 0)

        # Test with an order total equal to the start_price for rule2
        order_total_rule2 = 75
        expected_discount_rule2 = (15 / 100) * order_total_rule2
        self.assertEqual(self.sample_rule2.apply_discount(order_total_rule2), expected_discount_rule2)

        # Test with an order total greater than the start_price for rule2 but less than rule3
        order_total_rule2 = 80
        expected_discount_rule2 = (15 / 100) * order_total_rule2
        self.assertEqual(self.sample_rule2.apply_discount(order_total_rule2), expected_discount_rule2)

        # Test with an order total less than the start_price for rule3
        order_total_rule3 = 90
        self.assertEqual(self.sample_rule3.apply_discount(order_total_rule3), 0)

        # Test with an order total equal to the start_price for rule3
        order_total_rule3 = 100
        expected_discount_rule3 = (20 / 100) * order_total_rule3
        self.assertEqual(self.sample_rule3.apply_discount(order_total_rule3), expected_discount_rule3)

        # Test with an order total greater than the start_price for rule3
        order_total_rule3 = 110
        expected_discount_rule3 = (20 / 100) * order_total_rule3
        self.assertEqual(self.sample_rule3.apply_discount(order_total_rule3), expected_discount_rule3)

    def test_rule_unique_constraint(self):
        # Test if the unique constraint on coupon, discount_percentage, and start_price is enforced
        with self.assertRaises(IntegrityError):
            CouponRule.objects.create(
                coupon=self.sample_coupon,
                discount_percentage=10,
                start_price=50
            )

    def test_rule_string_representation(self):
        # Test the string representation of the CouponRule model
        expected_str_rule1 = f'{self.sample_coupon} - 10% off if order total is >= 50'
        self.assertEqual(str(self.sample_rule1), expected_str_rule1)


class OrderItemModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_product_test_data(cls)
        # Set up a sample order for testing
        cls.order = Order.objects.create(
            customer=None,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='+1234567890',
            order_note='Test Order',
            completed=False,
            coupon_price=0,
            tracking_code='',
            datetime_payed=None,
            datetime_delivered=None
        )

        # Add two OrderItem objects
        cls.order_item1 = OrderItem.objects.create(
            product=cls.product1,
            order=cls.order,
            quantity=2,
        )

        # order_item2 with product2 color_size=color2, size1 and additional_cost=50 with not discount
        color_size_obj1 = cls.product2.color_size_values.get(color=cls.color2, size=cls.size1)
        color_size_obj1.additional_cost = 50
        color_size_obj1.save()
        cls.order_item2 = OrderItem.objects.create(
            product=cls.product2,
            order=cls.order,
            color_size=color_size_obj1,
            quantity=3,
        )
        # order_item3 with product5 color_size=color2, size2 and additional_cost=10 with discount
        color_size_obj2 = cls.product5.color_size_values.create(color=cls.color2, size=cls.size2)
        color_size_obj2.additional_cost = 10
        color_size_obj2.save()
        cls.order_item3 = OrderItem.objects.create(
            product=cls.product5,
            order=cls.order,
            color_size=color_size_obj2,
            quantity=3,
        )
        # order_item4 with product2 color_size=color1, size1
        cls.order_item4 = OrderItem.objects.create(
            product=cls.product2,
            order=cls.order,
            color_size=cls.product2.color_size_values.get(color=cls.color1, size=cls.size1),
            quantity=3,
        )

    def test_order_item_model_attributes(self):
        # None color_size
        self.assertEqual(self.order_item1.product, self.product1)
        self.assertIsNone(self.order_item1.color_size)
        self.assertEqual(self.order_item1.order, self.order)
        self.assertEqual(self.order_item1.quantity, 2)
        self.assertEqual(self.order_item1.track_order, OrderItem.TRACK_ORDER_UNPAID)
        self.assertIsNone(self.order_item1.datetime_processing)
        self.assertIsNone(self.order_item1.datetime_process_finished)
        self.assertEqual(self.order_item1.price, 100)
        self.assertTrue(self.order_item1.discount)
        self.assertEqual(self.order_item1.discount_price, 70)
        # Not None color_size with not additional_cost
        self.assertEqual(self.order_item4.price, 150)
        self.assertFalse(self.order_item4.discount)
        self.assertIsNone(self.order_item4.discount_price)
        # Not None color_size with additional_cost with no discount
        self.assertEqual(self.order_item2.price, 200)  # 150 + 50(additional_cost)
        self.assertFalse(self.order_item2.discount)
        self.assertIsNone(self.order_item2.discount_price)
        # Not None color_size with additional_cost with discount
        self.assertEqual(self.order_item3.price, 210)  # 200 + 10(additional_cost)
        self.assertTrue(self.order_item3.discount)
        self.assertEqual(self.order_item3.discount_price, 160)  # 150 + 10(additional_cost)

    def test_order_item_string_representation(self):
        expected_str = f'order number: {self.order.pk}'
        self.assertEqual(str(self.order_item2), expected_str)

    def test_order_item_total_properties(self):
        # None color_size With discount
        self.assertEqual(self.order_item1.get_total_no_discount_item, 200)  # 2 * 100
        self.assertEqual(self.order_item1.get_total_with_discount_item, 140)  # 2 * 70
        self.assertEqual(self.order_item1.get_total_profit_item, 60)  # (2 * 100) - (2 * 70)
        self.assertEqual(self.order_item1.get_total_item, 140)  # no_discount_item - profit_item
        # Not None color_size with additional_cost with no discount
        self.assertEqual(self.order_item2.get_total_no_discount_item, 600)  # 3 * (150 + 50)
        self.assertEqual(self.order_item2.get_total_with_discount_item, 0)  # No discount applied
        self.assertEqual(self.order_item2.get_total_profit_item, 0)  # No discount applied
        self.assertEqual(self.order_item2.get_total_item, 600)  # No discount applied

    def test_order_item_unique_constraint(self):
        # Test if the unique_together constraint is enforced
        with self.assertRaises(IntegrityError):
            OrderItem.objects.create(
                product=self.product1,
                order=self.order,
                quantity=1
            )

    def test_valid_color_size_for_product_order_item(self):
        # invalid color_size for product1
        with self.assertRaises(ValidationError):
            OrderItem.objects.create(
                product=self.product1,
                color_size=self.product2.color_size_values.first(),
                order=self.order,
                quantity=1
            )


class OrderModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_product_test_data(cls)
        # Set up a sample order for testing
        cls.order = Order.objects.create(
            customer=cls.user,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='+1234567890',
            order_note='Test order note',
        )

        # Set up a sample coupon for testing
        cls.sample_coupon = Coupon.objects.create(
            code='TESTCODE',
            start_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=7),
            num_available=10,
            num_used=5,
            reason_make="Test Coupon",
            is_active=True
        )

        # Set up three sample rules for testing
        cls.sample_rule1 = CouponRule.objects.create(
            coupon=cls.sample_coupon,
            discount_percentage=10,
            start_price=500
        )

        cls.sample_rule2 = CouponRule.objects.create(
            coupon=cls.sample_coupon,
            discount_percentage=15,
            start_price=750
        )

        # item1 without color_size
        cls.item1 = OrderItem.objects.create(order=cls.order, product=cls.product1, quantity=2)
        # item2 with color_size
        color_size_value1 = cls.product2.color_size_values.get(color=cls.color1, size=cls.size1)
        cls.item2 = OrderItem.objects.create(order=cls.order, product=cls.product2, color_size=color_size_value1,
                                             quantity=3)
        # item3 with color_size and additional_cost
        color_size_value2 = cls.product3.color_size_values.first()
        color_size_value2.additional_cost = 70
        color_size_value2.save()
        cls.item3 = OrderItem.objects.create(order=cls.order, product=cls.product3, color_size=color_size_value2,
                                             quantity=1)

    def test_order_model_attributes(self):
        self.assertEqual(self.order.customer, self.user)
        self.assertEqual(self.order.first_name, 'John')
        self.assertEqual(self.order.last_name, 'Doe')
        self.assertEqual(self.order.email, 'john.doe@example.com')
        self.assertEqual(self.order.phone, '+1234567890')
        self.assertEqual(self.order.order_note, 'Test order note')
        self.assertFalse(self.order.completed)
        self.assertEqual(self.order.coupon_price, 0)
        self.assertEqual(self.order.tracking_code, '')
        self.assertIsNotNone(self.order.datetime_created)
        self.assertIsNotNone(self.order.datetime_updated)

    def test_order_str_method(self):
        self.assertEqual(str(self.order), f'{self.order.pk}')

    def test_order_get_absolute_url(self):
        expected_url = reverse('store:order_detail', args=[self.order.pk])
        self.assertEqual(self.order.get_absolute_url(), expected_url)

    def test_order_act_items(self):
        items = self.order.act_items()
        self.assertEqual(list(items), [self.item1, self.item2, self.item3])

    def test_order_get_cart_items(self):
        self.assertEqual(self.order.get_cart_items, 6)

    def test_order_get_cart_total_no_discount(self):
        # product1 + product2 + (product3 with additional_cost)
        self.assertEqual(self.order.get_cart_total_no_discount, (2 * 100) + (3 * 150) + (1 * (120+70)))

    def test_order_get_cart_total_profit(self):
        # product1 + product2 + product3
        self.assertEqual(self.order.get_cart_total_profit, (2 * (100 - 70)) + 0 + 0)

    def test_order_get_cart_total(self):
        # product1 + product2 + (product3 with additional_cost)
        self.assertEqual(self.order.get_cart_total, (2 * 70) + (3 * 150) + (1 * (120+70)))

    def test_order_get_cart_total_with_coupon(self):
        # None coupon
        self.assertFalse(self.order.calculate_coupon_price(request=None, success_message=False))
        self.assertEqual(self.order.get_cart_total_with_coupon, 0)
        # Set coupon
        self.order.coupon = self.sample_coupon
        self.order.save()
        # Test order price with coupon
        self.assertTrue(self.order.calculate_coupon_price(request=None, success_message=False))
        # order coupon price must set with calculate_coupon_price
        expected_coupon_price = (15 / 100) * self.order.get_cart_total
        self.assertEqual(self.order.coupon_price, expected_coupon_price)
        # test get_cart_total_with_coupon
        self.assertEqual(self.order.get_cart_total_with_coupon, self.order.get_cart_total - self.order.coupon_price,)

    def test_order_avg_track_items(self):
        self.item1.track_order = 50
        self.item2.track_order = 80
        self.item1.save()
        self.item2.save()
        self.assertEqual(self.order.avg_track_items, _('Out for delivery'))

    def test_remove_inactive_product_from_order(self):
        # test signal order_signals.py/remove_inactive_product_from_order_items
        self.product2.is_active = False
        self.product2.save()
        items = self.order.items.all()
        self.assertEqual(list(items), [self.item1, self.item3])

        # test again with inventory 0
        self.product1.inventory = 0
        self.product1.save()
        items = self.order.items.all()
        self.assertEqual(list(items), [self.item3])


class ShippingAddressModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create necessary objects for testing
        cls.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        cls.order = Order.objects.create(
            customer=cls.user,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone='+1234567890',
            order_note='Test Order',
        )

        cls.shipping_address = ShippingAddress.objects.create(
            order=cls.order,
            state='Test State',
            city='Test City',
            address='Test Address',
            plate=123
        )

    def test_shipping_address_model_attributes(self):
        self.assertEqual(str(self.shipping_address), self.shipping_address.address)
        self.assertEqual(self.shipping_address.order, self.order)
        self.assertEqual(self.shipping_address.state, 'Test State')
        self.assertEqual(self.shipping_address.city, 'Test City')
        self.assertEqual(self.shipping_address.address, 'Test Address')
        self.assertEqual(self.shipping_address.plate, 123)
        self.assertIsNotNone(self.shipping_address.datetime_created)
        self.assertIsNotNone(self.shipping_address.datetime_updated)

    def test_unique_order_constraint(self):
        with self.assertRaises(IntegrityError):
            ShippingAddress.objects.create(
                order=self.order,
                state='create a shipping address for same order',
                city='create a shipping address for same order',
                address='create a shipping address for same order',
                plate=123
            )
