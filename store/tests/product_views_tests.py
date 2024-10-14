from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

import json

from ..models import Product, Category, ProductColor, ProductSize, ProductSpecification
from ..utils import sort_product_queryset


def create_product_test_data(cls):
    # Create some test data, adjust as needed
    # Create three categories
    cls.category1 = Category.objects.create(name='Category 1', slug_change=False)
    cls.category2 = Category.objects.create(name='Category 2', slug_change=False)
    cls.category3 = Category.objects.create(name='Category 3', slug_change=False)

    # Create five products
    cls.product1 = Product.objects.create(title='Product 1', short_description='short description for product 1',
                                          price=100, inventory=10, discount=True, discount_price=70, is_active=True)
    cls.product2 = Product.objects.create(title='Product 2', short_description='short description for product 2',
                                          price=150, inventory=15, is_active=True)
    cls.product3 = Product.objects.create(title='Product 3', short_description='short description for product 3',
                                          price=120, inventory=12, is_active=True)
    cls.product4 = Product.objects.create(title='Product 4', short_description='short description for product 4',
                                          price=80, inventory=8, is_active=True)
    cls.product5 = Product.objects.create(title='Product 5', short_description='short description for product 5',
                                          price=200, inventory=20, discount=True, discount_price=150, is_active=True)
    cls.product6 = Product.objects.create(title='Product 6', short_description='short description for product 6',
                                          price=7000, inventory=20, is_active=True)
    cls.product7 = Product.objects.create(title='Product 7', short_description='short description for product 7',
                                          price=800, inventory=20, discount=True, discount_price=70, is_active=False)
    cls.product8 = Product.objects.create(title='Product 8', short_description='short description for product 8',
                                          price=70, inventory=0, is_active=True)
    # Add category to products
    cls.product1.category.add(cls.category1)
    cls.product1.category.add(cls.category3)
    cls.product2.category.add(cls.category2)
    cls.product3.category.add(cls.category3)

    # Create two colors
    cls.color1 = ProductColor.objects.create(name='Red', color='#FF0000')
    cls.color2 = ProductColor.objects.create(name='Green', color='#00FF00')

    # Create two sizes
    cls.size1 = ProductSize.objects.create(size='Small')
    cls.size2 = ProductSize.objects.create(size='Large')

    # Manually choose colors, sizes, or both for product2, product3, and a hypothetical product6
    cls.product2.color_size_values.create(color=cls.color1, size=cls.size1)
    cls.product2.color_size_values.create(color=cls.color1, size=cls.size2)
    cls.product2.color_size_values.create(color=cls.color2, size=cls.size1)
    cls.product3.color_size_values.create(color=cls.color2, size=cls.size2)
    cls.product4.color_size_values.create(size=cls.size1)
    cls.product6.color_size_values.create(color=cls.color1)

    # Create a sample user for testing
    cls.user = get_user_model().objects.create_user(
        username='testuser',
        password='testpassword'
    )


class ProductsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_product_test_data(cls)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/products/list/')  # Update with your actual URL
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertTemplateUsed(response, 'store/product/product_list.html')

    def test_view_returns_products(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 6)
        self.assertContains(response, 'Product 1')
        self.assertContains(response, self.product1.short_description)
        product2_color_size_value = self.product2.color_size_values.all().first()
        self.assertContains(response, product2_color_size_value.color.color)
        self.assertContains(response, product2_color_size_value.size.size)

    def test_view_returns_filtered_products(self):
        # Test 2: Filter by color, size, sort by price
        response = self.client.get(reverse('store:product_list'),
                                   {'color': self.color1.name, 'size': self.size2.size, 'sort': '1'})
        products = response.context['products']
        self.assertEqual(len(products), 3)  # Assuming there are fewer than 2 products for this combination o

        # Test 3: Filter by color, size, sort by price descending
        response = self.client.get(reverse('store:product_list'),
                                   {'color': self.color1.name, 'size': self.size2.size, 'sort': '2'})
        products = response.context['products']
        self.assertEqual(len(products), 3)
        self.assertEqual(products[0], self.product6)

        # Test 4: Filter by color, size, sort by price descending
        response = self.client.get(reverse('store:product_list'),
                                   {'color': self.color1.name, 'size': self.size2.size, 'consider_both': True,
                                    'sort': '2'})
        products = response.context['products']
        self.assertEqual(len(products), 1)  # Assuming there are fewer than 2 products for this combination o

        # Test 5: Filter by different color, size, sort by price
        response = self.client.get(reverse('store:product_list'),
                                   {'color': self.color2.name, 'size': self.size2.size, 'sort': '1'})
        products = response.context['products']
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0], self.product3)

    def test_view_returns_sorted_products(self):
        for num in ['1', '2', '3', '4']:
            response = self.client.get(reverse('store:product_list'), {'sort': num})
            products = response.context['products']
            product_order_by_key = sort_product_queryset(num, Product.active_objs.all())
            self.assertEqual(products[0], product_order_by_key.first())

    def test_view_context_contains_filterset(self):
        response = self.client.get(reverse('store:product_list'))
        self.assertIsNotNone(response.context['filter'])

    def test_view_context_contains_liked_products(self):
        # Assuming you have an authenticated user for this test
        self.client.force_login(self.user)
        response = self.client.get(reverse('store:product_list'))
        self.assertIn('liked', response.context)


class ProductSearchViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_product_test_data(cls)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/products/search/')  # Update with your actual URL
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('store:product_search'))
        self.assertEqual(response.status_code, 200)

    def test_view_displays_search_results(self):
        # Test with a valid query
        response = self.client.get(reverse('store:product_search'), {'q': 'Product'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/product/search_page.html')
        self.assertContains(response, 'Product 1')
        self.assertContains(response, self.product1.short_description)
        self.assertContains(response, 'Product 2')
        product2_color_size_value = self.product2.color_size_values.all().first()
        self.assertContains(response, product2_color_size_value.color.color)
        self.assertContains(response, product2_color_size_value.size.size)

        # Test with an empty query
        response_empty_query = self.client.get(reverse('store:product_search'))
        self.assertEqual(response_empty_query.status_code, 200)
        self.assertTemplateUsed(response_empty_query, 'store/product/search_q_none.html')

    def test_view_context_contains_search_query(self):
        # Test with a valid query
        response = self.client.get(reverse('store:product_search'), {'q': 'Product'})
        self.assertEqual(response.context['q'], 'Product')
        self.assertEqual(len(response.context['products']), 6)

        # Test search product work correctly
        response = self.client.get(reverse('store:product_search'), {'q': 'Product 3'})
        self.assertEqual(response.context['products'][0], self.product3)

        # Test inactive products
        response = self.client.get(reverse('store:product_search'), {'q': 'Product 7'})
        self.assertEqual(len(response.context['products']), 0)

        # Test with an empty query
        response_empty_query = self.client.get(reverse('store:product_search'))
        self.assertIsNone(response_empty_query.context.get('q'))

    def test_view_returns_filtered_products(self):
        # Test 2: Filter by color, size, sort by price
        response = self.client.get(reverse('store:product_search'),
                                   {'q': 'product', 'color': self.color1.name, 'size': self.size2.size, 'sort': '1'})
        products = response.context['products']
        self.assertEqual(len(products), 3)  # Assuming there are fewer than 2 products for this combination o

        # Test 3: Filter by color, size, sort by price descending
        response = self.client.get(reverse('store:product_search'),
                                   {'q': 'product', 'color': self.color1.name, 'size': self.size2.size, 'sort': '2'})
        products = response.context['products']
        self.assertEqual(len(products), 3)
        self.assertEqual(products[0], self.product6)

        # Test 4: Filter by color, size, sort by price descending
        response = self.client.get(reverse('store:product_search'),
                                   {'q': 'product', 'color': self.color1.name, 'size': self.size2.size,
                                    'consider_both': True,
                                    'sort': '2'})
        products = response.context['products']
        self.assertEqual(len(products), 1)  # Assuming there are fewer than 2 products for this combination o

        # Test 5: Filter by different color, size, sort by price
        response = self.client.get(reverse('store:product_search'),
                                   {'q': 'product', 'color': self.color2.name, 'size': self.size2.size, 'sort': '1'})
        products = response.context['products']
        self.assertEqual(len(products), 2)
        self.assertEqual(products[0], self.product3)

    def test_view_returns_sorted_products(self):
        for num in ['1', '2', '3', '4']:
            response = self.client.get(reverse('store:product_search'), {'sort': num, 'q': 'product'})
            products = response.context['products']
            product_order_by_key = sort_product_queryset(num, Product.active_objs.all())
            self.assertEqual(products[0], product_order_by_key.first())

    def test_view_context_contains_filterset(self):
        response = self.client.get(reverse('store:product_search'), {'q': 'product', })
        self.assertIsNotNone(response.context['filter'])

    def test_view_context_contains_liked_products(self):
        # Assuming you have an authenticated user for this test
        self.client.force_login(self.user)
        response = self.client.get(reverse('store:product_search'), {'q': 'product', })
        self.assertIn('liked', response.context)


class ProductDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_product_test_data(cls)

        # Create three colors
        cls.color3 = ProductColor.objects.create(name='Purple', color='#800080')

        # Create three sizes
        cls.size3 = ProductSize.objects.create(size='XX-Small')

        # choose colors and sizes for product1 and product2 and product3
        cls.product1.color_size_values.create(color=cls.color1, size=cls.size1)
        cls.product1.color_size_values.create(color=cls.color1, size=cls.size2)
        cls.product2.color_size_values.create(color=cls.color3, size=cls.size3)
        cls.product3.color_size_values.create(color=cls.color1, size=cls.size2)

        # create two specification
        cls.specification1 = ProductSpecification.objects.create(name='weight')
        cls.specification2 = ProductSpecification.objects.create(name='dimensions')

        # set specification for product1
        cls.product1.specs_values.create(specification=cls.specification1, value='12kg specification')
        cls.product1.specs_values.create(specification=cls.specification2, value='10*10*10 mm specification')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/products/{self.product1.slug}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('store:product_detail', args=[self.product2.slug]))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('store:product_detail', args=[self.product1.slug]))
        self.assertTemplateUsed(response, 'store/product/product_detail.html')

    def test_404_for_inactive_product(self):
        # product7 is_active is False
        response = self.client.get(reverse('store:product_detail', args=[self.product7.slug]))
        self.assertEqual(response.status_code, 404)

        # product8 inventory is 0
        response = self.client.get(reverse('store:product_detail', args=[self.product8.slug]))
        self.assertEqual(response.status_code, 404)

    def test_view_displays_product_details(self):
        response = self.client.get(reverse('store:product_detail', args=[self.product1.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['product'], self.product1)
        # title
        self.assertContains(response, 'Product 1')
        self.assertContains(response, self.product1.description)
        self.assertContains(response, self.product1.short_description)
        self.assertContains(response, self.product1.category.all().first().name)
        self.assertContains(response, self.specification1.name)
        self.assertContains(response, self.specification2.name)
        # specification values
        self.assertContains(response, '12kg specification')
        self.assertContains(response, '10*10*10 mm specification')

    def test_view_displays_related_products(self):
        response = self.client.get(reverse('store:product_detail', args=[self.product1.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('related_products', response.context)
        related_products = response.context['related_products']
        self.assertEqual(len(related_products), 1)

    def test_view_requires_login_to_post_comment(self):
        response = self.client.post(reverse('store:product_detail', args=[self.product1.slug]),
                                    {'text': 'Test Comment'})
        self.assertEqual(response.status_code, 302)  # Should redirect to login page

    def test_view_allows_logged_in_user_to_post_comment(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('store:product_detail', args=[self.product1.slug]),
                                    {'text': 'Test Comment', 'star': '4'})
        self.assertEqual(response.status_code, 302)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)


class FavoriteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user
        cls.user = get_user_model().objects.create_user(username='testuser', password='testpassword')

        # Create a test product
        cls.product = Product.objects.create(title='Test Product', price=100, inventory=10, is_active=True)

    def test_favorite_view_authenticated_user_likes_product(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('store:set_favorite_product'), json.dumps({'productId': self.product.pk}),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['authenticated'])
        self.assertTrue(get_user_model().objects.get(pk=self.user.pk).fav_products.filter(pk=self.product.pk).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)

    def test_favorite_view_authenticated_user_unlikes_product(self):
        self.client.force_login(self.user)
        self.product.favorite.add(self.user)

        response = self.client.post(reverse('store:set_favorite_product'), json.dumps({'productId': self.product.pk}),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['authenticated'])
        self.assertFalse(get_user_model().objects.get(pk=self.user.pk).fav_products.filter(pk=self.product.pk).exists())

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)

    def test_favorite_view_with_invalid_product_pk(self):
        self.client.force_login(self.user)

        # response for like product
        response = self.client.post(reverse('store:set_favorite_product'),
                                    json.dumps({'productId': self.product.pk + 10}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

        self.product.favorite.add(self.user)
        # response for unlike product
        response = self.client.post(reverse('store:set_favorite_product'),
                                    json.dumps({'productId': self.product.pk + 10}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_favorite_view_unauthenticated_user_redirects_to_login(self):
        response = self.client.post(reverse('store:set_favorite_product'), json.dumps({'productId': self.product.pk}),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['authenticated'])
        self.assertIn(reverse('account_login'), response.json()['login'])

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)

    def test_favorite_view_invalid_json_request(self):
        self.client.force_login(self.user)
        self.product.favorite.add(self.user)

        response = self.client.post(reverse('store:set_favorite_product'), data='invalid_json_data',
                                    content_type='application/json')

        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)


class ProductUserLikedViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
        cls.user = get_user_model().objects.create_user(username='testuser', password='testpass')

        # Create categories
        cls.category1 = Category.objects.create(name='Category 1', slug_change=False)
        cls.category2 = Category.objects.create(name='Category 2', slug_change=False)

        # Create products
        cls.product1 = Product.objects.create(title='Product 1', price=100, inventory=10, is_active=True)
        cls.product2 = Product.objects.create(title='Product 2', price=150, inventory=15, is_active=True)

        # Add categories to products
        cls.product1.category.add(cls.category1)
        cls.product2.category.add(cls.category2)

        # Associate products with the user's favorites
        cls.user.fav_products.add(cls.product1)

    def setUp(self):
        # Log in the user for each test
        self.client.force_login(self.user)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('store:favorite_product_list'))
        self.assertTemplateUsed(response, 'store/product/product_list_user_like.html')

    def test_product_user_liked_view_with_liked_products(self):
        response = self.client.get(reverse('store:favorite_product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['products'], [self.product1])

    def test_product_user_liked_view_with_no_liked_products(self):
        # Remove the product from the user's favorites
        self.user.fav_products.remove(self.product1)

        response = self.client.get(reverse('store:favorite_product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 0)

    def test_product_user_liked_view_with_multiple_liked_products(self):
        # Add another product to the user's favorites
        self.user.fav_products.add(self.product2)

        response = self.client.get(reverse('store:favorite_product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), len(self.user.fav_products.all()))
        self.assertIn(response.context['products'][0], self.user.fav_products.all())
        self.assertIn(response.context['products'][1], self.user.fav_products.all())

    def test_product_user_liked_view_with_unauthenticated_user(self):
        self.client.logout()

        response = self.client.get(reverse('store:favorite_product_list'))
        self.assertRedirects(response, reverse('account_login') + '?next=' + reverse('store:favorite_product_list'))


class FilterSizeBasedColorViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_product_test_data(cls)

    def test_filter_size_based_color_view_valid_request(self):
        data = {
            'productId': self.product2.pk,
            'colorId': self.color1.pk
        }

        response = self.client.post(reverse('store:filter_size_ajax'), data=json.dumps(data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['sizeIds']), 2)
        self.assertIn(str(self.size1.pk), response.json()['sizeIds'])
        self.assertIn(str(self.size2.pk), response.json()['sizeIds'])

    def test_filter_size_based_color_view_invalid_json_request(self):
        response = self.client.post(reverse('store:filter_size_ajax'), data='invalid_json_data',
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Something went wrong')

    def test_filter_size_based_color_view_invalid_request_no_data(self):
        response = self.client.post(reverse('store:filter_size_ajax'), data=json.dumps({}),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Something went wrong')

    def test_filter_size_based_color_view_with_invalid_product(self):
        # product3 is_active is False
        data = {
            'productId': self.product7.pk,
            'colorId': self.color1.pk,
        }
        response = self.client.post(reverse('store:filter_size_ajax'), data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

        # product4 inventory is 0
        data = {
            'productId': self.product8.pk,
            'colorId': self.color1.pk,
        }
        response = self.client.post(reverse('store:filter_size_ajax'), data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

        # invalid product pk
        data = {
            'productId': self.product1.pk + 100,
            'colorId': self.color1.pk,
        }
        response = self.client.post(reverse('store:filter_size_ajax'), data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_filter_size_based_color_view_invalid_request_no_color(self):
        data = {
            'productId': self.product1.pk,
            'colorId': None
        }

        response = self.client.post(reverse('store:filter_size_ajax'), data=json.dumps(data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['sizeIds']), 0)
