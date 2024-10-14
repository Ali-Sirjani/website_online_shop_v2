from django.test import TestCase
from django.db import IntegrityError
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from ..models import Tag, TopTag, Post, PostComment


class TagModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.tag1 = Tag.objects.create(name='Test Tag 1')
        cls.tag2 = Tag.objects.create(name='Test Tag 2')

    def test_tag_attributes(self):
        self.assertEqual(self.tag1.name, 'Test Tag 1')
        self.assertEqual(self.tag1.slug, slugify(self.tag1.name))
        self.assertIsNotNone(self.tag1.datetime_created)
        self.assertIsNotNone(self.tag1.datetime_updated)
        self.assertEqual(str(self.tag1), self.tag1.name)

        # test tag get_absolute_url
        self.assertEqual(self.tag2.get_absolute_url(), reverse('blog:tag_list', args=[self.tag2.slug]))

    def test_unique_name(self):
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name=self.tag2.name)


class TopTagModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.tag1 = Tag.objects.create(name='Test Tag 1')
        cls.tag2 = Tag.objects.create(name='Test Tag 2')
        cls.top_tag1 = TopTag.objects.create(tag=cls.tag1, level='1', is_top_level=True)

    def test_top_tag_attributes(self):
        self.assertEqual(self.top_tag1.tag, self.tag1)
        self.assertIn(self.top_tag1.level, [choice[0] for choice in TopTag.LEVEL_CHOICES])
        self.assertTrue(self.top_tag1.is_top_level)
        self.assertIsNotNone(self.top_tag1.datetime_created)
        self.assertIsNotNone(self.top_tag1.datetime_updated)
        # test str
        expected_object_name = f'{self.top_tag1.tag}'
        self.assertEqual(expected_object_name, str(self.top_tag1))

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            TopTag.objects.create(tag=self.tag1, level='1', is_top_level=True)


class PostModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.user = get_user_model().objects.create_user(username='testuser', password='12345')
        cls.tag = Tag.objects.create(name='Test Tag')
        cls.post = Post.objects.create(
            author=cls.user,
            title='Test Post',
            description='Test Description',
            can_published=True,
            image='static/img/for_test/test1.jpg',
        )
        cls.post.tags.add(cls.tag)

    def test_post_attributes(self):
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.description, 'Test Description')
        self.assertTrue(self.post.can_published)
        self.assertFalse(self.post.slug_change)
        self.assertTrue(self.post.slug)
        self.assertIsNotNone(self.post.datetime_created)
        self.assertIsNotNone(self.post.datetime_updated)
        # str
        self.assertEqual(str(self.post), self.post.title)

    def test_post_tags_relationship(self):
        self.assertIn(self.tag, self.post.tags.all())

    def test_post_absolute_url(self):
        expected_url = reverse('blog:post_detail', args=[self.post.slug])
        self.assertEqual(self.post.get_absolute_url(), expected_url)

    def test_active_objects_manager(self):
        # Create an unpublished post
        unpublished_post = Post.objects.create(
            author=self.user,
            title='Unpublished Post',
            description='Test Description',
            can_published=False,
            slug_change=False
        )

        # Ensure it's not in the active objects queryset
        self.assertNotIn(unpublished_post, Post.active_objs.all())


class PostCommentModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.user = get_user_model().objects.create_user(username='testuser', password='12345')
        cls.post = Post.objects.create(author=cls.user, title='Test Post', description='Test Description', can_published=True, slug_change=False)
        cls.comment = PostComment.objects.create(post=cls.post, author=cls.user, text='Test Comment')

    def test_comment_attributes(self):
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.text, 'Test Comment')
        self.assertFalse(self.comment.confirmation)
        self.assertIsNotNone(self.comment.datetime_created)
        self.assertIsNotNone(self.comment.datetime_updated)
        # str
        expected_str = f'author: {self.comment.author}, post pk: {self.comment.post.pk}'
        self.assertEqual(str(self.comment), expected_str)

    def test_comment_parent_relationship(self):
        self.assertIsNone(self.comment.parent)

    def test_comment_absolute_url(self):
        expected_url = reverse('blog:post_detail', args=[self.post.slug])
        self.assertEqual(self.comment.get_absolute_url(), expected_url)
