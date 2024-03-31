"""Testing routes on pytest project ya_news."""
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture as lf


STAT_OK = HTTPStatus.OK
STAT_NFOUND = HTTPStatus.NOT_FOUND
pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'name',
    (
        (lf('page_edit')),
        (lf('page_delete')),
    ),
)
def test_redirects(client, name, page_login, comment):
    """Перенаправление анонима на страницу авторизации."""
    expected_url = f'{page_login}?next={name}'
    assertRedirects(client.get(name), expected_url)


@pytest.mark.parametrize(
    'name_page, parametrize_client, expected_status',
    (
        (lf('home_page'), lf('not_author_client'), STAT_OK),
        (lf('home_page'), lf('client'), STAT_OK),
        (lf('page_detail'), lf('not_author_client'), STAT_OK),
        (lf('page_detail'), lf('client'), STAT_OK),
        (lf('page_login'), lf('not_author_client'), STAT_OK),
        (lf('page_login'), lf('client'), STAT_OK),
        (lf('page_logout'), lf('not_author_client'), STAT_OK),
        (lf('page_logout'), lf('client'), STAT_OK),
        (lf('page_signup'), lf('not_author_client'), STAT_OK),
        (lf('page_signup'), lf('client'), STAT_OK),
        (lf('page_edit'), lf('not_author_client'), STAT_NFOUND),
        (lf('page_edit'), lf('author_client'), STAT_OK),
        (lf('page_delete'), lf('not_author_client'), STAT_NFOUND),
        (lf('page_delete'), lf('author_client'), STAT_OK),
    )
)
def test_pages_availability_for_different_users(
    name_page,
    parametrize_client,
    expected_status
):
    """Тестируем все адреса на доступность для разных пользователей.

    Доступные для анонимных пользователей - 'client',
    авторов заметок - 'author_client'
    и пользователей - читателей, т.е. не авторов 'not_author_client'.

    В параметрах функции передаём reverse страницы, пользователя и статус,
    который ожидаем при запросе страницы.
    """
    response = parametrize_client.get(name_page)
    assert response.status_code == expected_status
