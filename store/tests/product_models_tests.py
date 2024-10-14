from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db import transaction

from ..models import Category, Product, ProductSpecification, ProductSpecificationValue, ProductColor, ProductSize, \
    ProductColorAndSizeValue, ProductImage, TopProduct, ProductComment


class CategoryModelTest(TestCase):
    # Create a sample category for testing
    @classmethod
    def setUpTestData(cls):
        cls.category1 = Category.objects.create(
            name='Test Category',
            slug_change=True,
        )
        cls.category2 = Category.objects.create(
            name='Test Category 2',
            slug_change=False,
            slug='category',
        )

    def test_category_model_attributes(self):
        # Test all data attributes of the Category model
        self.assertEqual(self.category1.name, 'Test Category')
        self.assertFalse(self.category1.slug_change)
        self.assertEqual(self.category1.slug, slugify(self.category1.name))
        self.assertIsNone(self.category1.parent)
        self.assertEqual(str(self.category1), 'Test Category')

        # Check if datetime_created and datetime_updated are not None
        self.assertIsNotNone(self.category1.datetime_created)
        self.assertIsNotNone(self.category1.datetime_updated)

        # Check if get_absolute_url returns the correct URL
        expected_url = reverse('store:category_page', args=[self.category1.slug])
        self.assertEqual(self.category1.get_absolute_url(), expected_url)

    def test_category_children_related_name(self):
        # Test if the related name for children is set correctly
        child_category = Category.objects.create(
            name='Child Category',
            slug_change=True,
            slug='child-category',
            parent=self.category1
        )
        self.assertIn(child_category, self.category1.children.all())
        self.assertTrue(self.category1.is_leaf_node)

    def test_unique_name_constraint(self):
        # Test if the unique constraint on the name field is enforced
        with self.assertRaises(IntegrityError):
            Category.objects.create(
                name='Test Category',
                slug_change=True,
                slug='another-test-category'
            )

    def test_category_slug_signal(self):
        # Test if slug be empty
        category_empty_slug = Category.objects.create(
            name='empty-slug',
            slug_change=True,
            slug=''
        )
        self.assertNotEqual(category_empty_slug.slug, '')

        # Test if the unique constraint on slug is enforced (product_signals.py)
        category_slug_test = Category.objects.create(
            name='Another Test Category',
            slug_change=True,
            slug='test-category'
        )
        self.assertNotEqual(category_slug_test.slug, self.category1.slug)

        # Test generate slug based on name
        # before set slug_change slug is 'category'
        self.assertNotEqual(self.category2.slug, slugify(self.category2.name))
        self.category2.slug_change = True
        self.category2.save()
        # after set slug_change slug is based on category name
        self.assertEqual(self.category2.slug, slugify(self.category2.name))

        # Test again generate slug based on name
        # slug must be same
        self.category2.slug_change = True
        self.category2.save()
        self.assertEqual(self.category2.slug, slugify(self.category2.name))


class ProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sample user for testing
        cls.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Create a sample category for testing
        cls.category = Category.objects.create(
            name='Test Category',
            slug_change=True,
        )

        # Create a sample product for testing
        cls.product1 = Product.objects.create(
            title='Test Product',
            description='This is a test product description.',
            short_description='Short description for test product.',
            price=100,
            discount=False,
            inventory=10,
            slug_change=False,
            slug='test-product',
            is_active=True
        )

        cls.product2 = Product.objects.create(
            title='Test Product number 2',
            description='This is a test 2.',
            short_description='Short description 2.',
            price=500,
            discount=False,
            inventory=2,
            slug='test-product-number-2-different-title',
            is_active=True
        )

        cls.product3 = Product.objects.create(
            title='inventory 0',
            description='inventory 0',
            short_description='inventory 0',
            price=5_000,
            discount=False,
            inventory=0,
            slug_change=True,
            slug='inventory-0',
            is_active=True
        )

        # Add the category and user to the product
        cls.product1.category.add(cls.category)
        cls.product1.favorite.add(cls.user)

    def test_product_attributes(self):
        # Test all data attributes of the Product model
        self.assertEqual(self.product1.title, 'Test Product')
        self.assertEqual(self.product1.description, 'This is a test product description.')
        self.assertEqual(self.product1.short_description, 'Short description for test product.')
        self.assertEqual(self.product1.price, 100)
        self.assertFalse(self.product1.discount)
        self.assertIsNone(self.product1.discount_price)
        self.assertIsNone(self.product1.discount_timer)
        self.assertEqual(self.product1.inventory, 10)
        # slug will set False for product_signal.py/create_slug_product
        self.assertFalse(self.product1.slug_change)
        self.assertEqual(self.product1.slug, 'test-product')
        self.assertTrue(self.product1.is_active)

        # Check if datetime_created and datetime_updated are not None
        self.assertIsNotNone(self.product1.datetime_created)
        self.assertIsNotNone(self.product1.datetime_updated)

        # Check if get_absolute_url returns the correct URL
        expected_url = reverse('store:product_detail', args=[self.product1.slug])
        self.assertEqual(self.product1.get_absolute_url(), expected_url)

    def test_product_favorite_users(self):
        # Test if the product has the correct number of favorite users
        self.assertEqual(self.product1.favorite.count(), 1)
        self.assertIn(self.user, self.product1.favorite.all())

    def test_product_category_relationship(self):
        # Test if the product is associated with the correct category
        self.assertEqual(self.product1.category.count(), 1)
        self.assertIn(self.category, self.product1.category.all())

    def test_active_objects_manager(self):
        # Test if the active objects manager filters out inactive products
        active_products = Product.active_objs.all()
        # product3 when created is_active set True but the signal
        # product_signals.py/set_products_inactive_for_inventory set it False
        self.assertNotIn(self.product3, active_products)
        self.assertIn(self.product1, active_products)

    def test_product_slug_signal(self):
        # Test if the slug is generated automatically when the field is empty
        product_without_slug = Product.objects.create(
            title='Product Without Slug',
            description='This product does not have a predefined slug.',
            price=75,
            inventory=20,
            is_active=True
        )
        self.assertNotEqual(product_without_slug.slug, '')

        # Test if the unique constraint on slug is enforced
        test_product_slug = Product.objects.create(
            title='Duplicate Slug Product',
            description='This product has a duplicate slug.',
            price=90,
            inventory=15,
            slug='test-product'
        )

        self.assertNotEqual(self.product1.slug, test_product_slug.slug)

        # Test generate slug based on name
        # before set slug_change slug is 'test-product-number-2'
        self.assertNotEqual(self.product2.slug, slugify(self.product2.title))
        self.product2.slug_change = True
        self.product2.save()
        # after set slug_change slug is based on product name
        self.assertEqual(self.product2.slug, slugify(self.product2.title))

        # Test again generate slug based on name
        # slug must be same
        self.product2.slug_change = True
        self.product2.save()
        self.assertEqual(self.product2.slug, slugify(self.product2.title))


class ProductSpecificationModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sample product specification for testing
        cls.specification1 = ProductSpecification.objects.create(name='Test Specification')

    def test_unique_name_constraint(self):
        # Test if the unique constraint on the name field is enforced
        with self.assertRaises(IntegrityError):
            ProductSpecification.objects.create(name='Test Specification')

    def test_str_method(self):
        # Test the __str__ method to ensure it returns the correct string representation
        self.assertEqual(str(self.specification1), 'Test Specification')


class ProductSpecificationValueModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create sample product and specification for testing
        cls.product = Product.objects.create(
            title='Test Product',
            description='This is a test product description.',
            price=100,
            inventory=10,
            is_active=True
        )
        cls.specification = ProductSpecification.objects.create(name='Test Specification for value')

        cls.value1 = ProductSpecificationValue.objects.create(
            product=cls.product,
            specification=cls.specification,
            value='Value 1'
        )

    def test_product_specification_value_attributes(self):
        # Test all data attributes of the ProductSpecificationValue model
        self.assertEqual(self.value1.product, self.product)
        self.assertEqual(self.value1.specification, self.specification)
        self.assertEqual(self.value1.value, 'Value 1')

    def test_unique_together_constraint(self):
        # Test if the unique_together constraint is enforced
        # Attempt to create another value with the same product and specification
        with self.assertRaises(IntegrityError):
            ProductSpecificationValue.objects.create(
                product=self.product,
                specification=self.specification,
                value='Value 2'
            )

    def test_str_method(self):
        # Test the __str__ method to ensure it returns the correct string representation
        self.assertEqual(str(self.value1), 'Value 1')


class ProductColorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sample product color for testing
        cls.color1 = ProductColor.objects.create(
            name='Test Color',
            color='#ff0000'  # Example color value
        )

    def test_product_color_attributes(self):
        # Test all data attributes of the ProductColor model
        self.assertEqual(self.color1.name, 'Test Color')
        self.assertEqual(self.color1.color, '#ff0000')

    def test_unique_name_and_color_constraint(self):
        # Test if the unique constraint on the name field is enforced
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductColor.objects.create(
                    name='Test Color',
                    color='#00ff00'  # Another example color value
                )

        # Test if the unique constraint on the color field is enforced
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProductColor.objects.create(
                    name='Test Color 2',
                    color='#ff0000'
                )

    def test_str_method(self):
        # Test the __str__ method to ensure it returns the correct string representation
        self.assertEqual(str(self.color1), 'Test Color')


class ProductSizeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sample product size for testing
        cls.size1 = ProductSize.objects.create(size='Small')

    def test_unique_size_constraint(self):
        # Test if the unique constraint on the size field is enforced
        with self.assertRaises(IntegrityError):
            ProductSize.objects.create(size='Small')

    def test_str_method(self):
        # Test the __str__ method to ensure it returns the correct string representation
        self.assertEqual(str(self.size1), 'Small')


class ProductColorAndSizeValueModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create sample product, color, and size for testing
        cls.product = Product.objects.create(
            title='Test Product',
            description='This is a test product description.',
            price=100,
            inventory=10,
            is_active=True
        )
        cls.color = ProductColor.objects.create(name='Test Color', color='#ff0000')
        cls.size = ProductSize.objects.create(size='Small')

        cls.value1 = ProductColorAndSizeValue.objects.create(
            product=cls.product,
            color=cls.color,
            size=cls.size,
            additional_cost=15,
            inventory=8,
            is_active=True
        )

    def test_product_color_and_size_value_attributes(self):
        # Test all data attributes of the ProductColorAndSizeValue model
        self.assertEqual(self.value1.product, self.product)
        self.assertEqual(self.value1.color, self.color)
        self.assertEqual(self.value1.size, self.size)
        self.assertEqual(self.value1.additional_cost, 15)
        self.assertEqual(self.value1.inventory, 8)
        self.assertTrue(self.value1.is_active)

    def test_unique_together_constraint(self):
        # Attempt to create another value with the same product, color, and size
        with self.assertRaises(IntegrityError):
            ProductColorAndSizeValue.objects.create(
                product=self.product,
                color=self.color,
                size=self.size,
                additional_cost=15,
                inventory=8,
                is_active=True
            )

    def test_str_method(self):
        # Test the __str__ method to ensure it returns the correct string representation
        expected_str_color_size = f'{self.color}--{self.size}'
        self.assertEqual(str(self.value1), expected_str_color_size)

        self.value1.color = None
        self.value1.save()
        expected_str_size = f'{self.size}'
        self.assertEqual(str(self.value1), expected_str_size)

        self.value1.size = None
        self.value1.color = self.color
        self.value1.save()
        expected_str_color = f'{self.color}'
        self.assertEqual(str(self.value1), expected_str_color)

        self.value1.size = None
        self.value1.color = None
        self.value1.save()
        expected_str_none = 'None'
        self.assertEqual(str(self.value1), expected_str_none)

    def test_active_objects_manager(self):
        # Test if the active objects manager filters out inactive values
        inactive_value = ProductColorAndSizeValue.objects.create(
            product=self.product,
            color=self.color,
            additional_cost=20,
            inventory=0,
            is_active=False
        )

        active_values = ProductColorAndSizeValue.active_objs.all()
        self.assertNotIn(inactive_value, active_values)
        self.assertIn(self.value1, active_values)


class ProductImageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create sample product for testing
        cls.product = Product.objects.create(
            title='Test Product',
            description='This is a test product description.',
            price=100,
            inventory=10,
            is_active=True
        )

        # Create sample product images for testing
        cls.image1 = ProductImage.objects.create(
            product=cls.product,
            image='static/img/for_test/test1.jpg',
            is_main=True
        )
        cls.image2 = ProductImage.objects.create(
            product=cls.product,
            image='static/img/for_test/test2.jpg',
            is_main=False
        )

    def test_product_image_attributes(self):
        # Test all data attributes of the ProductImage model
        self.assertEqual(self.image1.product, self.product)
        self.assertEqual(self.image1.image.url, '/media/static/img/for_test/test1.jpg')
        self.assertTrue(self.image1.is_main)
        self.assertIsNotNone(self.image1.datetime_created)
        self.assertIsNotNone(self.image1.datetime_updated)

    def test_ordering(self):
        # Test the ordering of product images, main images first
        images = ProductImage.objects.all()
        self.assertEqual(images[0], self.image1)  # Main image comes first

    def test_str_method(self):
        # Test the __str__ method to ensure it returns the correct string representation
        self.assertEqual(str(self.image1), str(self.image1.pk))

    def test_main_image_in_product(self):
        # Assert that the URL of the image1 is equal to the main image URL in the product
        self.assertEqual(self.image1.image.url, self.product.main_image())

        # Set the is_main attribute to False and save the image
        self.image1.is_main = False
        self.image1.save()

        # Assert that the main_image method returns None after setting the image as not main
        self.assertIsNone(self.product.main_image())


class TopProductModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create four sample products for testing
        cls.product1 = Product.objects.create(
            title='Product 1',
            description='Description for Product 1',
            price=100,
            inventory=10,
            is_active=True
        )
        cls.product2 = Product.objects.create(
            title='Product 2',
            description='Description for Product 2',
            price=150,
            inventory=8,
            is_active=True
        )
        cls.product3 = Product.objects.create(
            title='Product 3',
            description='Description for Product 3',
            price=120,
            inventory=0,
            is_active=True
        )
        cls.product4 = Product.objects.create(
            title='Product 4',
            description='Description for Product 4',
            price=200,
            inventory=15,
            is_active=False  # Inactive product
        )

        # Create corresponding TopProduct instances for the first three products
        cls.top_product1 = TopProduct.objects.create(
            product=cls.product1,
            level='1',
            is_top_level=True
        )
        cls.top_product2 = TopProduct.objects.create(
            product=cls.product2,
            level='2',
            is_top_level=True
        )
        cls.top_product3 = TopProduct.objects.create(
            product=cls.product3,
            level='3',
            is_top_level=False  # Not marked as top level
        )

    def test_top_product_attributes(self):
        # Test all data attributes of the TopProduct model
        self.assertEqual(str(self.top_product1), 'Product 1')
        expected_url = reverse('store:product_detail', args=[self.product1.slug])
        self.assertEqual(self.top_product1.get_absolute_url(), expected_url)
        self.assertTrue(self.top_product1.is_top_level)
        self.assertEqual(self.top_product2.level, '2')
        self.assertFalse(self.top_product3.is_top_level)

    def test_active_objects_manager(self):
        # Test if the active objects manager filters out inactive products
        active_top_products = TopProduct.active_objs.all()
        self.assertIn(self.top_product1, active_top_products)
        self.assertIn(self.top_product2, active_top_products)
        self.assertNotIn(self.top_product3, active_top_products)  # Inactive product

    def test_limit_choices_to(self):
        # Test the limit_choices_to in the product ForeignKey
        # Ensure that only active products with inventory > 0 are available for selection
        available_products = Product.objects.filter(**TopProduct.LIMIT_CHOICES_TO_PRODUCT)
        self.assertIn(self.product1, available_products)
        self.assertIn(self.product2, available_products)
        self.assertNotIn(self.product3, available_products)  # Product with inventory = 0
        self.assertNotIn(self.product4, available_products)  # Inactive product


class ProductCommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a sample user for testing
        cls.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )

        # Create a sample product for testing
        cls.product = Product.objects.create(
            title='Test Product',
            description='This is a test product description.',
            price=100,
            inventory=10,
            is_active=True
        )

        # Create a sample comment for testing
        cls.comment = ProductComment.objects.create(
            product=cls.product,
            author=cls.user,
            text='This is a test comment.',
            star='4',
            confirmation=True
        )

    def test_comment_attributes(self):
        # Test all data attributes of the ProductComment model
        self.assertEqual(str(self.comment), 'testuser')
        self.assertEqual(self.comment.get_absolute_url(), reverse('store:product_detail', args=[self.product.slug]))
        self.assertEqual(self.comment.star, '4')
        self.assertTrue(self.comment.confirmation)

    def test_comments_relation_with_user_and_product(self):
        # Test the related names and relationships with user and product
        self.assertIn(self.comment, self.user.comments.all())
        self.assertIn(self.comment, self.product.comments.all())

    def test_datetime_fields(self):
        # Test if datetime_created is not None
        self.assertIsNotNone(self.comment.datetime_created)

        # Test if datetime_updated is not None after saving the comment
        previous_updated_datetime = self.comment.datetime_updated
        self.comment.text = 'Updated comment text.'
        self.comment.save()
        self.assertNotEqual(self.comment.datetime_updated, previous_updated_datetime)
