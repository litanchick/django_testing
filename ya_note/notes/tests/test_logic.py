# Невозможно создать две заметки с одинаковым slug.
"""Tests logic in project 'ya_note' with unittest."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    """Class for testing create notes."""

    NOTE_TEXT = 'Текст заметки - 2'
    NOTE_TITLE = 'Заголовок заметки - 2'

    @classmethod
    def setUpTestData(cls):
        """Create data for testing create notes from diferent authors."""
        cls.user = User.objects.create(username='Некий пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.user
        )
        cls.url = reverse('notes:add', args=None)
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'author': cls.user
        }

    def test_anonymous_user_cant_create_note(self):
        """Testing only a logged-in user can create a note."""
        response = self.client.post(self.url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 1)

    def test_user_can_create_note(self):
        """Testing autocreate slug."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        note = Note.objects.get(title=self.NOTE_TITLE)
        self.assertEqual(note.slug, slugify(self.NOTE_TITLE))

    def test_user_cant_use_two_same_slug(self):
        """Testing is not possible to create two notes with the same slug."""
        self.form_data['slug'] = '2'
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 2)
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'2{WARNING}'
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)


class TestNoteEditDelete(TestCase):
    """Class for testing edit and delete notes."""

    NOTE_TEXT = 'Текст заметки - 2'
    NOTE_TITLE = 'Заголовок заметки - 2'

    @classmethod
    def setUpTestData(cls):
        """Create data for testing edit/delete note with diferent authors."""
        cls.author = User.objects.create(username='Автор заметки')
        cls.reader = User.objects.create(username='Читатель')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
            'author': cls.author
        }

    def test_author_can_delete_note(self):
        """Testing the user can edit and delete their own notes."""
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Testing the user cannot edit other people's notes."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_cant_edit_note_of_another_user(self):
        """Testing the user cannot delete other people's notes."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, 'Текст')
