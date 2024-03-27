"""Testing content in project 'ya_note' with unittest."""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContentNotes(TestCase):
    """Class for testing pages content."""

    HOME_URL = reverse('notes:home')

    @classmethod
    def setUpTestData(cls):
        """Create data for tests with diferent author for note."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Некий пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_notes_view_only_author(self):
        """Notes from one user do not include notes from another user."""
        users_notes_count = (
            (self.author, 1),
            (self.reader, 0),
        )
        urls = (
            'notes:list',
            'notes:home'
        )
        for user, count_notes in users_notes_count:
            self.client.force_login(user)
            for page in urls:
                with self.subTest(user=user):
                    url = reverse(page)
                    response = self.client.get(url)
                    object_list = response.context['object_list']
                    self.assertEqual(object_list.count(), count_notes)

    def test_notes_order(self):
        """Testing passing a note to a page in the object_list."""
        detail_url = reverse('notes:detail', args=(self.notes.slug,))
        response = self.client.get(detail_url)
        self.assertIn('object_list', response.context)
        notes = response.context['object_list']
        all_notes = notes.notes_set.all()
        all_id_notes = [notes.created for notes in all_notes]
        sorted_timestamps = sorted(all_id_notes)
        self.assertEqual(all_id_notes, sorted_timestamps)

    def test_is_form_in_pages(self):
        """Forms are transferred to the note creation and editing pages."""
        pages = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        self.client.force_login(self.author)
        for page, args in pages:
            with self.subTest(name=page, args=args):
                url = reverse(page, args=args)
                response = self.client.get(url)
                object_list = response.context
                self.assertIn('form', object_list)
