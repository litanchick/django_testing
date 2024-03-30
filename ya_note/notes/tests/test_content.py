"""Testing content in project 'ya_note' with unittest."""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class SetupData(TestCase):
    """Create data for all testing."""

    NOTE_TEXT = 'Текст заметки - 2'
    NOTE_TITLE = 'Заголовок заметки - 2'

    @classmethod
    def setUpTestData(cls):
        """Create data for tests with diferent author for note."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.user = User.objects.create(username='Некий пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

        cls.url_home = reverse('notes:home')
        cls.url_login = reverse('users:login')
        cls.url_logout = reverse('users:logout')
        cls.url_signup = reverse('users:signup')
        cls.url_list = reverse('notes:list')
        cls.url_add = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_detail = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_delete = reverse('notes:edit', args=(cls.note.slug,))

        cls.form_data = {
            'title': cls.NOTE_TITLE,
            'text': cls.NOTE_TEXT,
        }


class TestContentNotes(SetupData):
    """Class for testing pages content."""

    def test_notes_order(self):
        """Testing passing a note to a page in the object_list."""
        users_statuses = (
            (self.author_client, True),
            (self.reader_client, False),
        )
        for user, flag_is_list in users_statuses:
            with self.subTest(user=user):
                response = user.get(self.url_list)
                object_context = response.context['object_list']
                self.assertEqual(self.note in object_context, flag_is_list)

    def test_is_form_in_pages(self):
        """Forms are transferred to the note creation and editing pages."""
        pages = (
            (self.url_add),
            (self.url_edit)
        )
        for page in pages:
            with self.subTest(name=page):
                response = self.author_client.get(page)
                object_context = response.context
                self.assertIn('form', object_context)
                self.assertIsInstance(response.context['form'], NoteForm)
