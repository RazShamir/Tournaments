from django.test import TestCase
from unittest import skip
from model_mommy import mommy
from models import Participants, Pool

# Create your tests here.

class StatisticsTest(TestCase):
    def setUp(self, *args, **kwargs):
        self.pool = mommy.make(Pool)

    def test_get_player_statistics(self):
        participant = mommy.make(Participants)
        self.pool.participants.add()


