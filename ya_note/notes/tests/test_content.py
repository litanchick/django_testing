"""Testing content in project 'ya_note' with unittest."""
from django.contrib.auth import get_user_model

from notes.forms import NoteForm

from .setup_test_data import SetupData


User = get_user_model()


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
