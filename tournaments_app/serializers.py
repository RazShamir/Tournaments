from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MinValueValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from tournaments_app.models import *
from datetime import datetime, timedelta

class SignupSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        max_length=128, validators=[validate_password], write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'read_only': True},
        }
        validators = [UniqueTogetherValidator(User.objects.all(), ['email'])]

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['email'],
                            email=validated_data['email'],
                            first_name=validated_data.get('first_name', ''),
                            last_name=validated_data.get('last_name', ''))
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', 'groups', 'last_login', 'user_permissions']


class TournamentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournaments
        # fields = '__all__'
        fields = ['id', 'name', 'created_at', 'creator', 'type']
        # exclude = ['pic_url']
        # depth = 1

class ParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participants
        fields = ['user']

class CreateTournamentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tournaments
        fields = ['name', 'type']
        validators = [
            UniqueTogetherValidator(
                queryset=Tournaments.objects.all(),
                fields=['name']
            )
        ]
    
    def create(self, validated_data):
        creator: User = self.context['creator']
        created_at = datetime.now()

        admin = None
        if 'admin' in validated_data:
            admin=validated_data['admin']
        else:
            admin = creator
        tour = Tournaments.objects.create(
            name=validated_data['name'],
            created_at=created_at,
            creator=creator,
            type=validated_data['type'],
            admin = admin
        )


        return tour
    

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['organization_name', 'organizer_id']
        validators = [
            UniqueTogetherValidator(
                queryset=Organization.objects.all(),
                fields=['organization_name']
            )
        ]


    def create(self, validated_data):
        if not 'organization_name' in validated_data:
            raise ValueError("Missing organization name")
        return Organization.objects.create(organization_name=validated_data['organization_name'],
                organizer_id=validated_data['organizer_id'])

class SignupTournametsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participants
        fields = ['tournament']
        validators = [
            UniqueTogetherValidator(
                queryset=Participants.objects.all(),
                fields=['tournament', 'user']
            )
        ]


    def create(self, validated_data):
        if 'user' in validated_data:
            return Participants.objects.create(tournament=validated_data['tournament'], user=validated_data['user'])
        else:
            if 'name' not in validated_data:
                raise ValueError("Missing name")
            else:
                return Participants.objects.create(tournament=validated_data['tournament'], name=validated_data['name'])