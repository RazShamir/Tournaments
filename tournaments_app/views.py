from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth.models import User, Group
from datetime import datetime, timedelta
from tournaments_app.game_type import GAME_TYPES
from django.db.models import Avg, Count
from django.contrib.auth.decorators import user_passes_test
from tournaments_app.utils import tournament_has_enough_participants, is_tournament_admin, is_tournament_organizer, delete_players_not_checked_in
from tournaments_app.models import * 
from tournaments_app.serializers import * 
from enum import Enum
from pathlib import Path
from tournaments_app import tournamentsViews



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


@api_view(['POST'])
def register_participant(request: Request, tournament_id):
    s = ParticipantsSerializer(data={   
                                        'username': request.user.username,
                                        # 'username': request.data['username'],
                                        'user': request.user.id,
                                        'tournament': tournament_id,
                                        'game_username': request.data['game_username']
                                            })
    # does this save/send participant id?
    s.is_valid(raise_exception=True)
    s.save()

    return JsonResponse(data={"status": "successfully registered"})

@api_view(['POST'])
def unregister_participant(request: Request, tournament_id):
    Participants.objects.filter(tournament_id=tournament_id, user=request.user.id).delete()
    return JsonResponse(data={"message": "You successfully unregistered"})

@api_view(['PUT'])
def check_in_participant(request: Request, tournament_id):
    participant = Participants.objects.filter(tournament_id=tournament_id, user=request.user.id).first()
    s = ParticipantsSerializer(instance=participant ,data={'checked_in': True, 'tournament': tournament_id, 'user': request.user.id
                                            })
    if s.is_valid(raise_exception=True):
        s.save()
    
    return JsonResponse(data={"message": "Checked in successfully"})