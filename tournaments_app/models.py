import datetime
from random import shuffle
from typing import List
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Tournaments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, unique=True)
    name = models.CharField(max_length=256, null=True)
    created_at = models.DateTimeField(blank=False, null=True)
    start_time = models.DateTimeField(blank=False, null=True)
    end_time = models.DateTimeField(blank=False, null=True, default=None)
    is_ongoing = models.BooleanField(blank=False, null=False, default=False)
    type = models.IntegerField(blank=False, null=False)
    details = models.TextField(default="")

    class Meta:
        db_table = 'tournaments'

    def get_participants(self):
        return Participants.objects.filter(tournament=self.id)


class Organization(models.Model):
    organizer_id = models.ForeignKey(User, on_delete=models.RESTRICT, blank=False, null=False)
    tournament = models.ForeignKey(
        Tournaments, on_delete=models.RESTRICT, blank=False, null=True)
    organization_name = models.CharField(max_length=256, null=False, default="")

    # TODO: add logo and description to model

    def __str__(self):
        return f"{self.organization_name}"

    class Meta:
        db_table = 'organization'


class OrganizationAdmin(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.RESTRICT, blank=True, null=True)
    organization_id = models.ForeignKey(
        Organization, on_delete=models.RESTRICT, blank=False, null=True)
    is_active = models.BooleanField(blank=False, null=False)

    def __str__(self):
        return f"Admin: '{self.user}' tournament: '{str(self.tournament)}'"

    class Meta:
        db_table = 'organization_admins'


class Participants(models.Model):
    id = models.BigAutoField(primary_key=True)
    participant_id = models.UUIDField(blank=False, null=False, default=uuid4(), max_length=256)
    tournament = models.ForeignKey(
        Tournaments, on_delete=models.RESTRICT, blank=False, null=False)
    user = models.ForeignKey(
        User, on_delete=models.RESTRICT, blank=True, null=True)
    score = models.IntegerField(blank=False, null=False, default=0)
    checked_in = models.BooleanField(default=False, null=False)
    game_username = models.CharField(max_length=256, default="")
    username = models.CharField(max_length=256, null=False, default="")
    active = models.BooleanField(default=True, null=False)

    def get_matches(self):
        return Match.objects.filter(participant_one=self.participant_id, participant_two=self.participant_id)

    def __str__(self):
        return self.game_username

    class Meta:
        db_table = 'participants'


class PlayerStats(models.Model):
    tournament = models.ForeignKey(Tournaments, on_delete=models.RESTRICT, blank=False, null=False)
    participant = models.ForeignKey(Participants, on_delete=models.RESTRICT, blank=False, null=False)
    score = models.IntegerField(blank=False, null=False, default=0)
    omw = models.FloatField(blank=False, null=False)

    @property
    def score(self):
        return self.score

    class Meta:
        db_table = 'statistics'


class Pool(models.Model):
    tournament = models.ForeignKey(Tournaments, on_delete=models.RESTRICT, unique=True)
    participants = models.ManyToManyField(Participants)

    @property
    def initial_round_exists(self) -> bool:
        return Rounds.objects.filter(round_num=1, tournament=self.tournament).exists()

    # views.py -> Pool.generate_matches()
    def create_initial_round(self) -> list:
        matches = []
        first_round = Rounds(tournament=self.tournament,
                             start_at=datetime.datetime.now(),
                             end_at=None,
                             round_num=1,
                             participant_pool=self)
        first_round.save()
        participants = list(self.participants.all())

        shuffle(participants)
        pool1, pool2 = participants[len(participants) / 2:], participants[:len(participants) / 2]
        for p1, p2 in zip(pool1, pool2):
            matches.append(Match(participant_one=p1, participant_two=p2, rounds=first_round))
        return matches

    def get_OMW(self, participant: Participants):
        opponents = Match.get_match_opponents(participant=participant)
        current_omw = []
        for opponent in opponents:
            opponent_statistics = PlayerStats.objects.get(participant=opponent.participant_id)
            opponent_score = opponent_statistics.score
            opponent_games_played = Match.get_number_of_games_played(opponent)
            current_omw.append(opponent_score / opponent_games_played)

        return round(current_omw)

    def get_standings(self):
        return PlayerStats.objects.filter(tournament=self.tournament.id).order_by("score", "omw")

    def get_player_stats(self, participant: Participants):
        return PlayerStats.objects.get(participant=participant.participant_id)

    def create_round(self) -> list:
        current_round = Rounds(tournament=self.tournament,
                               start_at=datetime.datetime.now(),
                               round_num=self.get_current_round_number() + 1,
                               end_at=None,
                               participant_pool=self)
        current_round.save()
        matches = []
        participants = list(self.participants.all())
        pool1, pool2 = participants[int(len(participants) / 2):], participants[:int(len(participants) / 2)]
        for p1, p2 in zip(pool1, pool2):
            matches.append(Match(participant_one=p1, participant_two=p2, rounds=current_round))
        return matches
        # 1. pair the players with the highest points
        # 2. two players cant play each other more than once

    def create_rounds(self) -> List:
        participant_count = self.participants.count()
        if participant_count % 2 != 0:
            self.participants.add(None)  # Match(p1=Participant, p2=None)
        if not self.initial_round_exists:
            return self.create_initial_round()

        return self.create_round()

        # check if Round(round_number=1) exists
        # add player shuffle (initial pairings)
        # calculate next rounds pairings
        # create new pairings after R1

    def get_current_round_number(self):
        return max(list(Rounds.objects.filter(tournament_id=self.tournament.id).values_list("round_num")))[0]


class Rounds(models.Model):
    tournament = models.ForeignKey(
        Tournaments, on_delete=models.RESTRICT, blank=False, null=False)
    start_at = models.DateTimeField(null=False, blank=False)
    end_at = models.DateTimeField(null=True, blank=True)
    round_num = models.IntegerField(null=False, blank=False)
    participant_pool = models.ForeignKey(Pool, on_delete=models.RESTRICT, blank=True, null=True)

    def __str__(self):
        return self.round_num

    class Meta:
        db_table = 'rounds'


class Match(models.Model):
    class MatchType(models.IntegerChoices):
        SWISS_BO1 = 1
        SINGLE_ELIMINATION_BO1 = 2
        SWISS_BO3 = 3
        SINGLE_ELIMINATION_BO3 = 4

    class Result(models.IntegerChoices):
        P1_W = 1
        P2_W = 2
        TIE = 3

    class MatchStatus(models.IntegerChoices):
        FINISHED = 1
        ONGOING = 2

    match_id = models.UUIDField(primary_key=True, default=uuid4())
    match_type = models.IntegerField(choices=MatchType.choices, default=MatchType.SWISS_BO1)
    participant_one = models.ForeignKey(Participants, on_delete=models.RESTRICT, related_name='first_participant')
    participant_two = models.ForeignKey(Participants, on_delete=models.RESTRICT, related_name='second_participant')
    participant_one_result = models.IntegerField(default=0)
    participant_two_result = models.IntegerField(default=0)
    rounds = models.ForeignKey(Rounds, on_delete=models.RESTRICT, blank=False, null=False)

    @property
    def is_tie(self) -> bool:
        return self.participant_one_result == self.participant_two_result

    @property
    def winner(self):
        if self.participant_one_result and self.participant_two_result == 0:
            return
        elif self.participant_one_result > self.participant_two_result:
            return self.participant_one
        elif self.participant_two_result > self.participant_one_result:
            return self.participant_two

    def result(self):
        if self.is_tie:
            PlayerStats.objects.filter(participant=self.participant_one).score += 1
            PlayerStats.objects.filter(participant=self.participant_two).score += 1
        else:
            PlayerStats.objects.filter(participant=self.winner).score += 3

    def get_number_of_games_played(participant: Participants) -> int:
        return Match.objects.filter(participant_one=participant.participant_id,
                                    participant_two=participant.participant_id).count()

    @staticmethod
    def get_match_history(participant: Participants):
        return Match.objects.filter(participant_one=participant.participant_id,
                                    participant_two=participant.participant_id)

    @staticmethod
    def get_match_opponents(participant: Participants) -> List[Participants]:
        opponenets = []
        opponenets.append(Match.objects.filter(participant_one=participant.participant_id).values("participant_two"))
        opponenets.append(Match.objects.filter(participant_two=participant.participant_id).values("participant_one"))
        return opponenets

    class Meta:
        db_table = 'matches'


class Notes(models.Model):
    tournament = models.ForeignKey(
        Tournaments, on_delete=models.RESTRICT, blank=False, null=True)
    note = models.CharField(null=False, blank=False)
    warning_type = models.CharField(null=False, blank=False)

    def __str__(self):
        return f"{self.note}"

    class Meta:
        db_table = 'notes'
