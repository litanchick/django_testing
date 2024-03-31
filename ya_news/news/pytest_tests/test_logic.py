"""Тестирование логики проекта 'ya_news' с помощью pytest."""
from http import HTTPStatus
from random import choice

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

FORM_DATA = {
    'text': 'Новый текст',
}
pytestmark = pytest.mark.django_db


def test_user_cant_use_bad_words(author_client, page_detail):
    """Если комментарий содержит запрещённые слова, форма вернёт ошибку."""
    count_comment_last = Comment.objects.count()
    bad_words_data = {
        'text': f'Какой-то текст,{choice(BAD_WORDS)}, еще текст'
    }
    response = author_client.post(page_detail, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == count_comment_last


def test_anonymous_user_cant_create_comment(client, page_detail):
    """Анонимный пользователь не может создать комментарий."""
    count_comment_last = Comment.objects.count()
    response = client.post(page_detail, data=FORM_DATA)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={page_detail}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == count_comment_last


def test_auth_user_can_add_comment(
        author_client,
        news,
        page_detail,
        comment
):
    """Зарегистрированный пользователь может отправлять заметки."""
    count_comment_last = Comment.objects.count()
    response = author_client.post(page_detail)
    assert response.status_code == HTTPStatus.OK
    assert Comment.objects.count() == count_comment_last
    comment_from_db = Comment.objects.last()
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author


def test_author_can_edit_comment(
        author_client,
        comment,
        page_edit,
        news,
        author
):
    """Тестирование редактирования комментария автором."""
    response = author_client.post(page_edit, FORM_DATA)
    assert response.status_code == HTTPStatus.FOUND
    comment = Comment.objects.get(id=comment.pk)
    comment.refresh_from_db()
    assert comment.text == FORM_DATA['text']
    assert comment.news == news
    assert comment.author == author


def test_other_user_cant_edit_comment(
        not_author_client,
        comment,
        news,
        page_edit
):
    """Зарегистрированный пользователь не может редактировать чужую заметку."""
    response = not_author_client.post(page_edit, FORM_DATA)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=news.pk)
    assert comment.news == comment_from_db.news
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author


def test_author_can_delete_comment(author_client, comment, page_delete, news):
    """Автор заметки может её удалить."""
    count_comment_last = Comment.objects.count()
    response = author_client.post(page_delete)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == count_comment_last - 1


def test_other_user_cant_delete_comment(
        not_author_client,
        comment,
        page_delete
):
    """Не автор не может удалить заметку."""
    count_comment_last = Comment.objects.count()
    response = not_author_client.post(page_delete)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == count_comment_last
