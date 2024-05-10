from django.test import TestCase

from control.models import Announce
from control.services import get_announces


class GetAnnouncesTestCase(TestCase):
    def setUp(self):
        self.announce1 = Announce.objects.create(
            title='test1',
            body='test1',
        )
        self.announce2 = Announce.objects.create(
            title='test2',
            body='test2',
        )
        self.announce3 = Announce.objects.create(
            title='test3',
            body='test3',
        )

    def test_announces(self):
        # Given:
        # When:
        all_announces = get_announces()

        # Then: All announces are returned
        self.assertEqual(all_announces.count(), 3)
        # And: Specific announces are returned
        self.assertEqual(
            set(all_announces.values_list('id', flat=True)),
            {self.announce1.id, self.announce2.id, self.announce3.id}
        )
