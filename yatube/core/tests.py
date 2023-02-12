from django.test import TestCase

from http import HTTPStatus


class ViewTestClass(TestCase):
    def test_error_page(self):
        """Проверьте, что статус ответа сервера - 404
        Проверьте, что используется шаблон core/404.html"""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
