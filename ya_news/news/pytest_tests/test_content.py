"""Тестируем контент на pytest проекта 'ya_news'."""
import pytest
from django.urls import reverse

FIRST_ELEMENT = 0


@pytest.mark.django_db
def test_news_count(count_news_pagination, client, limit_news_on_page):
    """Количество новостей не более 10 сортировка от свежим к старым."""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_page_count = len(object_list)
    assert news_page_count <= limit_news_on_page
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(news, pk_for_news, client, sort_list_comment):
    """Комментарии отсортированы в хронологическом порядке: старые в начале."""
    url = reverse('news:detail', args=pk_for_news)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps[FIRST_ELEMENT] == sorted_timestamps[FIRST_ELEMENT]


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, flag_availability_form',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_pages_contains_form(
    parametrized_client,
    flag_availability_form,
    pk_for_news
):
    """Проверяем доступность формы для анонимного пользователя и не анонима."""
    url = reverse('news:detail', args=pk_for_news)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is flag_availability_form
