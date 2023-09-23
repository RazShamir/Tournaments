from enum import Enum

from django.db.models import QuerySet
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from tournaments_app.serializers import *
from tournaments_app.utils import tournament_has_enough_participants, delete_players_not_checked_in


@api_view(['POST'])
def create_tournament(request: Request):
    user: User = request.user
    if user.is_staff:
        serializer = TournamentSerializer(
            data={'name': request.data['name'], 'type': request.data['type'],
                  'start_time': request.data['start_time'], 'details': request.data['details']})
        serializer.is_valid(raise_exception=True)
        tur: Tournaments = serializer.save()
        tur.save()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_401_UNAUTHORIZED)


def change_tournament_state(tournament: Tournaments):
    tournament_serializer = TournamentSerializer(instance=tournament, data={"is_ongoing": True})
    if tournament_serializer.is_valid():
        tournament_serializer.save()


@api_view(['POST'])
def start_tournament(request: Request, tournament_id):
    if tournament_has_enough_participants(tournament_id):
        tournament = Tournaments.objects.get(id=tournament_id)

        change_tournament_state(tournament)  # Now users cant register
        delete_players_not_checked_in(tournament_id)  # Now you have the real participant pool
        participants = tournament.get_participants()
        player_pool, created = Pool.objects.get_or_create(tournament=tournament)
        for participant in participants:
            player_pool.participants.add(participant)

        rounds = player_pool.create_rounds()
        print(rounds)


class MatchResult(Enum):
    win = 'win'
    loss = 'loss'
    tie = 'tie'


@api_view(['POST'])
def report_match_result(request: Request):
    match_result = request.data['result']
    future_time = datetime.now() + timedelta(seconds=15)


class TournamentType(str, Enum):
    upcoming = 'upcoming'
    ongoing = 'ongoing'
    completed = 'completed'
    other = 'other'

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


def get_tournament_by_type(tournament_type: str) -> QuerySet:
    match tournament_type:
        case TournamentType.upcoming:
            return Tournaments.objects.filter(start_time__gt=datetime.now())
        case TournamentType.ongoing:
            return Tournaments.objects.filter(start_time__lt=datetime.now(), is_ongoing=True)

        case TournamentType.completed:
            return Tournaments.objects.filter(start_time__lt=datetime.now(), is_ongoing=False)

        case _:
            return Tournaments.objects.filter(
                start_time__range=[datetime.now() - timedelta(days=7), datetime.now() + timedelta(days=7)])


def is_user_registered_to_tournament(user: User, tournament_id: uuid4) -> bool:
    return Participants.objects.filter(user_id=user.id, tournament_id=tournament_id).exists()


@api_view(['GET'])
def get_tournaments(request: Request, tournament_type: str = ''):
    tournaments = get_tournament_by_type(tournament_type)
    serializer = TournamentSerializer(instance=tournaments, many=True)
    for tournament in serializer.data:
        tournament.update({"is_registered": is_user_registered_to_tournament(request.user, tournament['id'])})

    return JsonResponse(data=serializer.data, safe=False)


@api_view(['GET'])
def get_tournament(request: Request, tournament_id) -> JsonResponse:
    tournament = Tournaments.objects.get(id=tournament_id)
    serializer = TournamentSerializer(instance=tournament, many=False)
    data = serializer.data.update(
        {'user_registered': is_user_registered_to_tournament(request.user, tournament_id)})
    return JsonResponse(data, safe=False)
