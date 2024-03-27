"""Тестирование логики проекта 'ya_news' с помощью pytest."""
from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

from .test_content import FIRST_ELEMENT


def test_user_cant_use_bad_words(author_client, pk_for_news):
    """Если комментарий содержит запрещённые слова, форма вернёт ошибку."""
    url = reverse('news:detail', args=pk_for_news)
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, pk_for_news):
    """Анонимный пользователь не может создать комментарий."""
    url = reverse('news:detail', args=pk_for_news)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_auth_user_can_add_comment(author_client, pk_for_news, comment):
    """Зарегистрированный пользователь может отправлять заметки."""
    url = reverse('news:detail', args=pk_for_news)
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
        author_client,
        form_data,
        pk_for_news,
        comment
):
    """Тестирование редактирования комментария автором."""
    url = reverse('news:edit', args=pk_for_news)
    response = author_client.post(url, form_data)
    assertRedirects(
        response,
        reverse(
            'news:detail',
            args=pk_for_news
        ) + '#comments'
    )
    comment.refresh_from_db()
    assert comment.news == form_data['news']
    assert comment.text == form_data['text']
    assert comment.author == form_data['author']


@pytest.mark.django_db
def test_other_user_cant_edit_comment(
        not_author_client,
        form_data, comment,
        pk_for_news
):
    """Зарегистрированный пользователь не может редактировать чужую заметку."""
    url = reverse('news:edit', args=pk_for_news)
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=pk_for_news[FIRST_ELEMENT])
    assert comment.news == comment_from_db.news
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, pk_for_comment, pk_for_news):
    """Автор заметки может её удалить."""
    url = reverse('news:delete', args=pk_for_comment)
    response = author_client.post(url)
    assertRedirects(
        response,
        reverse(
            'news:detail',
            args=pk_for_news
        ) + '#comments'
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_other_user_cant_delete_comment(
        not_author_client,
        pk_for_comment
):
    """Не автор не может удалить заметку."""
    url = reverse('news:delete', args=pk_for_comment)
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
