"""Tests logic in project 'ya_note' with unittest."""
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

from .test_content import SetupData

User = get_user_model()


class TestNoteCreation(SetupData):
    """Class for testing create notes."""

    def test_anonymous_user_cant_create_note(self):
        """Testing only a logged-in user can create a note."""
        note_count_last = Note.objects.count()
        response = self.client.post(self.url_add, data=self.form_data)
        expected_url = f'{self.url_login}?next={self.url_add}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), note_count_last)

    def test_user_can_create_note(self):
        """Testing autocreate slug and can create note."""
        response = self.author_client.post(self.url_add, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)
        note = Note.objects.last()
        self.assertEqual(note.slug, slugify(self.NOTE_TITLE))
        self.assertEqual(note.author, self.author)

    def test_user_cant_use_two_same_slug(self):
        """Testing is not possible to create two notes with the same slug."""
        self.form_data['slug'] = '2'
        response = self.auth_client.post(self.url_add, data=self.form_data)
        self.assertEqual(Note.objects.count(), 2)
        response = self.auth_client.post(self.url_add, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=f'2{WARNING}'
        )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 2)


class TestNoteEditDelete(SetupData):
    """Class for testing edit and delete notes."""

    def test_author_can_delete_and_edit_note(self):
        """Testing the user can edit and delete their own notes."""
        count_notes_last = Note.objects.count()
        response = self.author_client.post(self.url_edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), count_notes_last)
        object_context = Note.objects.last()
        self.assertEqual(object_context.text, self.NOTE_TEXT)
        self.assertEqual(object_context.title, self.NOTE_TITLE)
        self.assertEqual(object_context.author, self.author)
        note = Note.objects.last()
        url = reverse('notes:delete', args=(note.slug,))
        response = self.author_client.delete(url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), count_notes_last - 1)

    def test_user_cant_delete_note_of_another_user(self):
        """Testing the user cannot edit other people's notes."""
        response = self.reader_client.post(self.url_delete)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_user_cant_edit_note_of_another_user(self):
        """Testing the user cannot delete other people's notes."""
        response = self.reader_client.post(self.url_edit, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        object_context = Note.objects.last()
        self.assertEqual(object_context.text, 'Текст заметки')
        self.assertEqual(object_context.title, 'Заголовок')
        self.assertEqual(object_context.author, self.author)
