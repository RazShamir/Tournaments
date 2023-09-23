from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from tournaments_app.models import Tournaments, Participants
from tournaments_app.serializers import TournamentSerializer
from tournaments_app.config import MINIMUM_NUMBER_OF_PLAYERS

def is_tournament_admin(user: User) -> bool:
    return user.groups.filter(name="tournament_admin").exists()

def is_tournament_organizer(user: User) -> bool:
    return user.groups.filter(name="tournament_organizer").exists()

def tournament_has_enough_participants(tournament_id) -> bool:
    return Participants.objects.filter(tournament_id=tournament_id, checked_in=True).count() <= MINIMUM_NUMBER_OF_PLAYERS
    

def delete_players_not_checked_in(tournament_id):
    Participants.objects.filter(tournament_id=tournament_id,
                                checked_in=False).delete()

def does_tournament_need_bye(tournament_id) -> bool:
    return Participants.objects.filter(tournament_id=tournament_id, checked_in=True).count() % 2 == 1

def pair_players(tournament_id):
    pass


def update_tournament_state(tournament: Tournaments):
    tournament_serializer = TournamentSerializer(instance=tournament, data={"is_ongoing": True})
    if tournament_serializer.is_valid():
        tournament_serializer.save()

