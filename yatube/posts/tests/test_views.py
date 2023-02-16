# posts/tests/test_views.py
import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from django import forms

from posts.models import Post, Comment, Follow

from .factories import post_create, group_create, user_create

from http import HTTPStatus


User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth = user_create('auth')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = group_create()

        for i in range(13):
            cls.post = post_create(
                author=cls.auth,
                group=cls.group,
                image=cls.uploaded
            )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='V')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.auth_client = Client()
        self.auth_client.force_login(PostViewsTests.auth)
        self.kwargs_slug = {'slug': PostViewsTests.group.slug}
        self.kwargs_user = {'username': PostViewsTests.auth}
        self.kwargs_id = {'post_id': PostViewsTests.post.id}
        cache.clear()

    # Проверка Paginator
    def test_first_page_contains_ten_records(self):
        """10 постов на первой странице."""
        def response(name_url, kwr):
            return self.client.get(reverse(
                name_url,
                kwargs=kwr
            )).context['page_obj']
        self.assertEqual(len(response('posts:index', None)), 10)
        self.assertEqual(len(response('posts:group_list', self.kwargs_slug)),
                         10)
        self.assertEqual(len(response('posts:profile', self.kwargs_user)), 10)

    def test_second_page_contains_three_records(self):
        """3 поста на второй."""
        def response(name_url, kwr):
            return self.client.get(reverse(
                name_url,
                kwargs=kwr
            ) + '?page=2').context['page_obj']
        self.assertEqual(len(response('posts:index', None)), 3)
        self.assertEqual(len(response('posts:group_list', self.kwargs_slug)),
                         3)
        self.assertEqual(len(response('posts:profile', self.kwargs_user)), 3)

    # Проверка шаблонов
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        def url(url, **kwargs):
            return reverse(url, kwargs=kwargs)
        urls = [
            url('posts:index'),
            url('posts:group_list', slug=self.group.slug),
            url('posts:profile', username=self.user.username),
            url('posts:post_detail', post_id=self.post.id),
            url('posts:post_edit', post_id=self.post.id),
            url('posts:post_create'),
        ]
        templates = [
            'posts/index.html',
            'posts/group_list.html',
            'posts/profile.html',
            'posts/post_detail.html',
            'posts/create_post.html',
            'posts/create_post.html',
        ]
        for url, template in zip(urls, templates):
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_index_url_contains_post(self):
        """На главной странице пользователь __точно__
        увидит единственный пост (создаём в `setUpClass`)"""
        response = self.auth_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        page_values = {
            first_object.text: self.post.text,
            first_object.author: self.auth,
            first_object.group: self.group,
            first_object.image: self.post.image
        }
        for obj, vl in page_values.items():
            with self.subTest(vl=vl):
                self.assertEqual(obj, vl)

    def test_group_list_url_contains_group(self):
        """В шаблон group_list передаются посты группы (см `setUpClass`)"""
        response = self.auth_client.get(reverse(
            'posts:group_list', kwargs=self.kwargs_slug))
        first_object = response.context['page_obj'][0]
        group_context = response.context['group']
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.auth)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.image, self.post.image)
        self.assertEqual(group_context.title, self.group.title)
        self.assertEqual(group_context.slug, self.group.slug)
        self.assertEqual(group_context.description, self.group.description)

    def test_profile_url_contains_post(self):
        """В шаблон profile передается профиль пользователя (см `setUp`)"""
        response = self.auth_client.get(reverse(
            'posts:profile', kwargs=self.kwargs_user
        ))
        first_object = response.context['page_obj'][0]
        user_object = response.context['user_posts'][0]
        user = response.context['username']
        self.assertEqual(first_object.text, self.post.text)
        self.assertEqual(first_object.author, self.auth)
        self.assertEqual(first_object.group, self.group)
        self.assertEqual(first_object.image, self.post.image)
        self.assertEqual(user_object.text, self.post.text)
        self.assertEqual(user_object.author, self.auth)
        self.assertEqual(user_object.group, self.group)
        self.assertEqual(user_object.image, self.post.image)
        self.assertEqual(user, str(self.auth))

    def test_post_detail_url_contains_post(self):
        """В шаблон post_detail передается пост (см `setUpClass`)"""
        response = self.auth_client.get(reverse(
            'posts:post_detail', kwargs=self.kwargs_id
        ))
        post_object = response.context['post_detail'][0]
        self.assertEqual(post_object.text, self.post.text)
        self.assertEqual(post_object.author, self.auth)
        self.assertEqual(post_object.group, self.group)
        self.assertEqual(post_object.image, self.post.image)

    def test_post_create_edit_url_contains_post_and_group(self):
        """Создаст пост от имени пользователя, автор может изменять свой пост
        (см `setUpClass`)"""
        response = self.auth_client.get(reverse('posts:post_create'))
        response_edit = self.auth_client.get(reverse(
            'posts:post_edit', kwargs=self.kwargs_id
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
                form_field = response_edit.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)


class CommentViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = user_create('author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.group = group_create()

        cls.post = post_create(
            group=cls.group,
            author=cls.author
        )

    def setUp(self):
        self.user = user_create('user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.kwargs_post = {'post_id': self.post.id}

    def test_add_comment_for_guest(self):
        """Не авторизованный пользователь не может оставить комментарий"""
        response = self.client.get(
            reverse('posts:add_comment', kwargs=self.kwargs_post)
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_comment_for_auth_user(self):
        """Авторизированный пользователь может оставить комментарий"""
        response = self.authorized_client.get(
            reverse('posts:add_comment', kwargs=self.kwargs_post)
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        comments_count = Comment.objects.filter(post=self.post.pk).count()
        form_data = {
            'text': 'comment',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs=self.kwargs_post),
            data=form_data,
            follow=True
        )
        comments = Post.objects.filter(
            id=self.post.pk
        ).values_list('comments', flat=True)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs=self.kwargs_post
        ))
        self.assertEqual(comments.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                post=self.post.pk,
                author=self.user.pk,
                text=form_data['text']
            ).exists()
        )


class CacheViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = user_create('user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = group_create()
        cls.post = post_create(
            group=cls.group,
            author=cls.user
        )
        cache.clear()

    def test_cache_index(self):
        """Хранение и очищение кэша для index"""
        response = CacheViewsTest.authorized_client.get(reverse('posts:index'))
        posts = response.content
        post_create(
            text='new_post',
            author=self.user
        )
        response_old = CacheViewsTest.authorized_client.get(
            reverse('posts:index')
        )
        old_posts = response_old.content
        self.assertEqual(old_posts, posts)
        cache.clear()
        response_new = CacheViewsTest.authorized_client.get(
            reverse('posts:index')
        )
        new_posts = response_new.content
        self.assertNotEqual(old_posts, new_posts)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = user_create('user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.unfol = user_create('unfol')
        cls.unfol_client = Client()
        cls.unfol_client.force_login(cls.unfol)
        cls.author = user_create('author')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author)
        cls.post = post_create(
            author=cls.author
        )

    def setUp(self):
        self.kwargs_author = {'username': self.author}

    def test_authorized_follow(self):
        """Авторизованный пользователь может подписываться
        на других пользователей и отписываться от них"""
        FollowViewsTest.authorized_client.get(
            reverse('posts:profile_follow', kwargs=self.kwargs_author)
        )
        follower = Follow.objects.filter(
            user=FollowViewsTest.user,
            author=FollowViewsTest.author
        ).exists()
        self.assertTrue(follower)
        FollowViewsTest.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs=self.kwargs_author)
        )
        self.assertTrue(follower)

    def test_post_author_for_followers(self):
        """Новая запись автора появляется в ленте тех, кто на него подписан"""
        FollowViewsTest.authorized_client.get(
            reverse('posts:profile_follow', kwargs=self.kwargs_author)
        )
        response = FollowViewsTest.authorized_client.get(
            reverse('posts:follow_index')
        )
        page = response.context.get('page_obj').object_list
        self.assertEqual(len(response.context.get('page_obj').object_list), 1)
        self.assertIn(FollowViewsTest.post, page)
        post_create(
            text='Hi!',
            author=FollowViewsTest.author
        )
        cache.clear()
        response_new = FollowViewsTest.authorized_client.get(
            reverse('posts:follow_index')
        )
        page_new = response_new.context.get('page_obj').object_list
        self.assertEqual(len(
            response_new.context.get('page_obj').object_list
        ), 2)
        self.assertIn(FollowViewsTest.post, page_new)

    def test_post_author_for_unfollowers(self):
        """Новая запись автора не появляется в ленте тех, кто не подписан"""
        response_unfol = FollowViewsTest.unfol_client.get(
            reverse('posts:follow_index')
        )
        page_unfol = response_unfol.context.get('page_obj').object_list
        self.assertEqual(len(
            response_unfol.context.get('page_obj').object_list
        ), 0)
        self.assertNotIn(FollowViewsTest.post, page_unfol)
        post_create(
            text='Hi!',
            author=FollowViewsTest.author
        )
        cache.clear()
        response_unfol_new = FollowViewsTest.unfol_client.get(
            reverse('posts:follow_index')
        )
        page_unfol_new = response_unfol_new.context.get('page_obj').object_list
        self.assertEqual(len(
            response_unfol_new.context.get('page_obj').object_list
        ), 0)
        self.assertNotIn(FollowViewsTest.post, page_unfol_new)
