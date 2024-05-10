from django.test import TestCase

from chatgpt.models import Lesson
from chatgpt.services import get_lessons


class GetAnnouncesTestCase(TestCase):
    def setUp(self):
        self.lesson1 = Lesson.objects.create(
            summary='test1',
            body='test1',
        )
        self.lesson2 = Lesson.objects.create(
            summary='test2',
            body='test2',
        )
        self.lesson3 = Lesson.objects.create(
            summary='test3',
            body='test3',
        )

    def test_get_lessons(self):
        # Given:
        # When:
        all_lessons = get_lessons()

        # Then: All lessons are returned
        self.assertEqual(all_lessons.count(), 3)
        # And: Specific lessons are returned
        self.assertEqual(
            set(all_lessons.values_list('id', flat=True)),
            {self.lesson1.id, self.lesson2.id, self.lesson3.id}
        )
