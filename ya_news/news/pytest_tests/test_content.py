"""Тестируем контент на pytest проекта 'ya_news'."""
import pytest
from django.conf import settings
from news.forms import CommentForm
from .conftest import pytestmark


def test_news_count(client, home_page, count_news_pagination):
    """Количество новостей не более 10 сортировка от свежим к старым."""
    response = client.get(home_page)
    object_context = response.context['object_list']
    news_page_count = len(object_context)
    assert news_page_count == settings.NEWS_COUNT_ON_HOME_PAGE
    all_dates = [news.date for news in object_context]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(news, client, page_detail, sort_list_comment):
    """Комментарии отсортированы в хронологическом порядке: старые в начале."""
    response = client.get(page_detail)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.parametrize(
    'parametrized_client, flag_availability_form',
    (
        (pytest.lazy_fixture('not_author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_pages_contains_form(
    parametrized_client,
    flag_availability_form,
    page_detail
):
    """Проверяем доступность формы для анонимного пользователя и не анонима."""
    response = parametrized_client.get(page_detail)
    assert ('form' in response.context) is flag_availability_form
    if flag_availability_form == True:
        assert isinstance(response.context['form'], CommentForm)
