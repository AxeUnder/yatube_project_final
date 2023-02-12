# posts/tests/test_urls.py
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache


from http import HTTPStatus

from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='группа',
            slug='slug',
            description='описание',
        )
        cls.post = Post.objects.create(
            author=cls.auth,
            text='пост',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='Ivan')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.auth_client = Client()
        self.auth_client.force_login(PostURLTests.auth)
        self.kwargs_id = {'post_id': PostURLTests.post.id}
        cache.clear()

    def test_urls_pages(self):
        """Страницы доступные всем"""
        urls = [
            '/', f'/group/{PostURLTests.group.slug}/',
            f'/profile/{PostURLTests.auth.username}/',
            f'/posts/{PostURLTests.post.id}/'
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page(self):
        """Запрос к несуществующей странице ошибка 404"""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_pages_authorized(self):
        """Страницы доступные авторизованным пользователям"""
        urls = ['/create/', '/contact/', '/thank-you/']
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_post_edit(self):
        """Страница доступная автору поста"""
        response = self.auth_client.get(f'/posts/{PostURLTests.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.post.id}/edit/'
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs=self.kwargs_id
        ))

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_templates(self):
        """URL-адрес использует соответствующий шаблон"""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/slug/': 'posts/group_list.html',
            f'/profile/{PostURLTests.auth.username}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.id}/': 'posts/post_detail.html',
            f'/posts/{PostURLTests.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)
