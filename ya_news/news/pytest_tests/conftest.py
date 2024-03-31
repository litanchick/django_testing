"""Для тестирования понадобятся фикстуры следующие фикстуры.

- объекты двух пользователей — автора комментария и обычного пользователя,
- два клиента, авторизованных для обычного пользователя и автора,
- объект комментария и формы.
"""
from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture(autouse=True)
def db_access_for_all_tests(db):
    """Открываем доступ к БД для всех тестов."""
    pass


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
def count_news_pagination():
    """Создаём количество новостей на 1 больше ограничения на странице."""
    data = datetime.today()
    all_news = [
        News(
            title=f'Заголовок {index}',
            text='Текст.',
            date=data - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
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


@pytest.fixture
def home_page():
    """Просчитываем путь до главной страницы."""
    url_home_page = reverse('news:home')
    return url_home_page


@pytest.fixture
def page_detail(news):
    """Просчитываем путь до страницы с новостью."""
    url_page_detail = reverse('news:detail', args=(news.pk,))
    return url_page_detail


@pytest.fixture
def page_delete(comment):
    """Просчитываем путь до страницы удаления комментария."""
    url_page_delete = reverse('news:delete', args=(comment.pk,))
    return url_page_delete


@pytest.fixture
def page_edit(comment):
    """Просчитываем путь до страницы редактирования комментария."""
    url_page_edit = reverse('news:edit', args=(comment.pk,))
    return url_page_edit


@pytest.fixture
def page_login():
    """Просчитываем путь до страницы входа в аккаунт."""
    url_page_login = reverse('users:login')
    return url_page_login


@pytest.fixture
def page_logout():
    """Просчитываем путь до страницы выхода из аккаунта."""
    url_page_logout = reverse('users:logout')
    return url_page_logout


@pytest.fixture
def page_signup():
    """Просчитываем путь до страницы регистрации."""
    url_page_signup = reverse('users:signup')
    return url_page_signup
