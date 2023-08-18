import datetime
from typing import Any
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from uuid import uuid4


# Create your models here.


class Tournaments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4,editable=False,unique=True)
    name = models.CharField(max_length=256, null=False)
    created_at = models.DateField(blank=False, null=False)
    type = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return f"Tournament: '{self.name}' created at: '{str(self.created_at)}'"

    class Meta:
        db_table = 'tournaments'


class Organization(models.Model):
    organizer_id = models.ForeignKey(User, on_delete=models.RESTRICT, blank=False, null=False)
    tournament = models.ForeignKey(
        Tournaments, on_delete=models.RESTRICT, blank=False, null=True)
    organization_name = models.CharField(max_length=256, null=False, default="")

    #TODO: add logo and description to model

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
    participant_id = models.CharField(blank=False, null=False, default=uuid4(), max_length=256)
    tournament = models.ForeignKey(
        Tournaments, on_delete=models.RESTRICT, blank=False, null=False)
    user = models.ForeignKey(
        User, on_delete=models.RESTRICT, blank=True, null=True)
    score = models.IntegerField(blank=False, null=False)
    checked_in = models.BooleanField(default=False, null=False)
    name = models.CharField(max_length=256, null=False, default="")
    active = models.BooleanField(default=True, null=False)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if (self.user != None):
            name = self.user.first_name + " " + self.user.last_login

    def __str__(self):
        return f"Participants: '{self.user}' score: '{str(self.score)}'"

    class Meta:
        db_table = 'participants'


class Rounds(models.Model):
    tournament = models.ForeignKey(
        Tournaments, on_delete=models.RESTRICT, blank=False, null=False)
    start_at = models.DateField(null=False, blank=False)
    end_at = models.DateField(null=False, blank=False)
    round_num = models.IntegerField(null=False, blank=False)

    def __str__(self):
        return f"Round"

    class Meta:
        db_table = 'rounds'


class Pairings(models.Model):
    player1 = models.ForeignKey(
        User, related_name="player1", on_delete=models.RESTRICT, blank=False, null=False)
    player2 = models.ForeignKey(
        User, related_name="player2", on_delete=models.RESTRICT, blank=False, null=False)
    result_p1 = models.IntegerField(
        null=False, name="result_p1", blank=False, default=0)
    result_p2 = models.IntegerField(
        null=False, name="result_p2", blank=False, default=0)
    final_score = models.IntegerField(blank=False, null=False, default=0)
    round = models.ForeignKey(
        Rounds, on_delete=models.RESTRICT, blank=False, null=False)
    checked_in_P1 = models.BooleanField(null=False, default=False)
    checked_in_P2 = models.BooleanField(null=False, default=False)

    def __str__(self):
        return f"Pair"

    class Meta:
        db_table = 'pairings'


class Notes(models.Model):
    tournament = models.ForeignKey(
        Tournaments, on_delete=models.RESTRICT, blank=False, null=True)
    note = models.CharField(null=False, blank=False)
    warning_type = models.CharField(null=False, blank=False)

    def __str__(self):
        return f"{self.note}"

    class Meta:
        db_table = 'notes'
