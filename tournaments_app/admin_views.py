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
from tournaments_app.utils import is_tournament_admin, is_tournament_organizer
from tournaments_app.models import * 
from tournaments_app.serializers import * 
from enum import Enum
from pathlib import Path

# @user_passes_test(is_tournament_admin) TODO fix this

@api_view(['POST'])
def delete_participant(request: Request, tournament_id):
    name = request.data['name']
    Participants.objects.filter(tournament_id=tournament_id, name=name).delete()
    return JsonResponse(data={"message": "Participant has been removed"})