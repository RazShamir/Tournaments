from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth.models import User, Group

from tournaments_app.game_type import GAME_TYPES
from django.db.models import Avg, Count
from django.contrib.auth.decorators import user_passes_test
from tournaments_app.utils import is_tournament_admin, is_tournament_organizer
from tournaments_app.models import * 
from tournaments_app.serializers import * 

# Create your views here.

@api_view(['POST'])
@user_passes_test(is_tournament_organizer)
def create_organization(request: Request):
    user: User = request.user
    organization_group, created = Group.objects.get_or_create(name=request.data['organization_name'])
    if created:
        user.groups.add(organization_group)
        organization_serializer = OrganizationSerializer(data={
            'organization_name': request.data['organization_name'],
            'organizer_id': user.id
            })
        organization_serializer.is_valid(raise_exception=True)
        org: Organization = organization_serializer.save()
        org.save()
    return Response(data={"message": "organization created", "extra": repr(org)}, status=status.HTTP_201_CREATED)
    
@api_view(['GET', 'POST'])
def create_tournment(request: Request):
    user: User = request.user
    if request.method == 'POST':
        if user.is_staff:
            serializer = CreateTournamentSerializer(
                data=request.data,
                context= {'creator': user})
            serializer.is_valid(raise_exception=True)
            tur: Tournaments = serializer.save()
            tur.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status = status.HTTP_401_UNAUTHORIZED)
    else:
        all_tournaments = Tournaments.objects.all()
        print("initial query:", all_tournaments.query)

        if 'name' in request.query_params:
            all_tournaments = all_tournaments.filter(name__iexact=request.query_params['name'])
            print("after adding name filter", all_tournaments.query)
        if 'created_at' in request.query_params:
            all_tournaments = all_tournaments.filter(created_at__gte=request.query_params['created_at'])
            print("after adding duration_from filter", all_tournaments.query)
        if 'creator' in request.query_params:
            all_tournaments = all_tournaments.filter(creator__iexact=request.query_params['creator'])
            print("after adding duration_to filter", all_tournaments.query)
        if 'type' in request.query_params:
            all_tournaments = all_tournaments.filter(type=GAME_TYPES[request.query_params['type']])
            print("after adding description filter", all_tournaments.query)

        serializer = TournamentsSerializer(instance=all_tournaments, many=True)
        return Response(data=serializer.data)

@api_view(['POST'])
def signup_tournaments(request):
    s = SignupTournametsSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    s.save()

    return Response(data=s.data)
