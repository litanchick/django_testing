"""Для тестирования понадобятся фикстуры следующие фикстуры.

- объекты двух пользователей — автора комментария и обычного пользователя,
- два клиента, авторизованных для обычного пользователя и автора,
- объект комментария и формы.
"""
import pytest

from django.test.client import Client
from yanews.settings import NEWS_COUNT_ON_HOME_PAGE
from django.utils import timezone
from news.models import Comment, News

from datetime import datetime, timedelta


@pytest.fixture
def limit_news_on_page():
    """Константа для количества новостей на странице."""
    limit_news_on_page: int = 10
    return limit_news_on_page


@pytest.fixture
def author(django_user_model):
    """Создаём пользователя автора комментариев."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """Создаём пользователя читателя комментариев."""
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    """Регистрируем пользователя автора в клиенте."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """Регистрируем пользователя не автора в клиенте."""
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """Создаём новость в БД для тестов."""
    news = News.objects.create(
        title='Заголовок',
        text='Текст'
    )
    return news


@pytest.fixture
def pk_for_news(news):
    """Создаём прямое обращение к id новости для url."""
    return news.pk,


@pytest.fixture
def count_news_pagination():
    """Создаём количество новостей на 1 больше ограничения на странице."""
    data = datetime.today()
    all_news = [
        News(
            title=f'Заголовок {index}',
            text='Текст.',
            date=data - timedelta(days=index))
        for index in range(NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(author, news):
    """Создаём комментарий от автора в БД для тестов."""
    comment = Comment.objects.create(
        news=news,
        text='Текст',
        author=author,
    )
    return comment


@pytest.fixture
def form_data(news, author):
    """Данные отправки POST запроса в форму для тестов."""
    return {
        'news': news,
        'author': author,
        'text': 'Новый текст',
    }


@pytest.fixture
def pk_for_comment(comment):
    """Создаём прямое обращение к id комментария для url."""
    return comment.pk,


@pytest.fixture
def sort_list_comment(news, author):
    """Создаём 10 комментариев, чтобы проверить сортировку."""
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст комментария {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
