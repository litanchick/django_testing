"""Testing routes on pytest project ya_news."""
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('pk_for_news')),
        ('news:delete', pytest.lazy_fixture('pk_for_news')),
    ),
)
def test_redirects(client, name, args):
    """Перенаправление анонима на страницу авторизации."""
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('pk_for_news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
     )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """Тестируем все адреса, доступные для анонимных пользователей."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    (
        ('news:edit'),
        ('news:delete')
    )
)
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, pk_for_comment, expected_status
):
    """Доступность редактирования, удаления комментария автору/не автору."""
    url = reverse(name, args=pk_for_comment)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status
