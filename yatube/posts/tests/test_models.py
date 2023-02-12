# posts/tests/tests_models.py
from django.test import TestCase
from posts.models import Group, Post
from django.contrib.auth import get_user_model


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Группа по интересам',
            slug='слаг',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Пост',
        )
        cls.long_post = Post.objects.create(
            author=cls.user,
            text='Не более 15 символов может уместиться в превью'
        )

    def test_models_have_object_names_contains_post_and_group(self):
        """У моделей корректно работает __str__(см `setUpClass`)"""
        group = PostModelTest.group
        post = PostModelTest.post
        long_post = PostModelTest.long_post
        self.assertEqual(str(group), 'Группа по интересам')
        self.assertEqual(str(post), 'Пост')
        self.assertEqual(str(long_post), 'Не более 15 сим')

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
