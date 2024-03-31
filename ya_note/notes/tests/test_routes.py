"""Testing routes in project 'ya_note' with unittest."""
from http import HTTPStatus

from django.contrib.auth import get_user_model

from .setup_test_data import SetupData

User = get_user_model()


class TestRoutes(SetupData):
    """Class for testing routes."""

    def test_pages_availability(self):
        """Testing availability pages project for all users."""
        urls = (
            (self.url_home),
            (self.url_login),
            (self.url_logout),
            (self.url_signup),
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete_and_detail(self):
        """Testing HTTPstatus for difrent permission users."""
        users_statuses = (
            (self.url_edit, self.author_client, HTTPStatus.OK),
            (self.url_delete, self.author_client, HTTPStatus.OK),
            (self.url_detail, self.author_client, HTTPStatus.OK),
            (self.url_add, self.author_client, HTTPStatus.OK),
            (self.url_success, self.author_client, HTTPStatus.OK),
            (self.url_list, self.author_client, HTTPStatus.OK),
            (self.url_edit, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.url_delete, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.url_detail, self.reader_client, HTTPStatus.NOT_FOUND),
            (self.url_add, self.reader_client, HTTPStatus.OK),
            (self.url_success, self.reader_client, HTTPStatus.OK),
            (self.url_list, self.reader_client, HTTPStatus.OK),
        )
        for url, user, status in users_statuses:
            with self.subTest(user=user, name=url):
                response = user.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Testing redirect with pages don't availability for anonymous."""
        urls = (
            (self.url_list),
            (self.url_success),
            (self.url_add),
            (self.url_detail),
            (self.url_edit),
            (self.url_delete),
        )
        for name in urls:
            with self.subTest(name=name):
                redirect_url = f'{self.url_login}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)
