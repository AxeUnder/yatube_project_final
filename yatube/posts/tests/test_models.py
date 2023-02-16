# posts/tests/tests_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache

from .factories import post_create, group_create, user_create


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = user_create('auth')
        cls.group = group_create(
            title='Группа по интересам',
            slug='слаг',
            description='Описание группы',
        )
        cls.post = post_create(
            author=cls.user,
            text='Пост',

        )
        cls.long_post = post_create(
            author=cls.user,
            text='Не более 15 символов может уместиться в превью'
        )

    def setUp(self):
        cache.clear()

    def test_models_have_object_names_contains_post_and_group(self):
        """У моделей корректно работает __str__(см `setUpClass`)"""
        self.assertEqual(str(self.group), 'Группа по интересам')
        self.assertEqual(str(self.post), 'Пост')
        self.assertEqual(str(self.long_post), 'Не более 15 сим')

    def test_verbose_name(self):
        """verbose_name в полях совпадает с Post."""
        def verboses(field):
            return self.post._meta.get_field(field).verbose_name
        self.assertEqual(verboses('text'), 'Текст поста')
        self.assertEqual(verboses('created'), 'Дата публикации')
        self.assertEqual(verboses('group'), 'Группа')
        self.assertEqual(verboses('author'), 'Автор')

    def test_help_text(self):
        """help_text в полях совпадает с Post."""
        def help(field):
            return self.post._meta.get_field(field).help_text
        self.assertEqual(help('text'), 'Введите текст поста')
        self.assertEqual(
            help('group'),
            'Группа, к которой будет относиться пост'
        )
