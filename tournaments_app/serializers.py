from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MinValueValidator
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from rest_framework_simplejwt.serializers import TokenObtainSerializer, TokenObtainPairSerializer
from tournaments_app.models import *
from datetime import datetime, timedelta, date
from tournaments_app.game_type import GAME_TYPES


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        user = User.objects.filter(pk=self.user.id).first()
        if user:
            data['username'] = user.username

        return data


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['match_id', 'participant_one', 'participant_two', 'participant_one_result', 'participant_two_result', 'rounds']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'username']
        extra_kwargs = {
            'email': {'required': True},

        }
        validators = [UniqueTogetherValidator(User.objects.all(), ['email'])]

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
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


class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournaments
        fields = "__all__"
        validators = [
            UniqueTogetherValidator(
                queryset=Tournaments.objects.all(),
                fields=['name']
            )
        ]

    def validate(self, data):
        if not GAME_TYPES.has_value(data['type']):
            raise serializers.ValidationError('type is invalid')

        if timezone.now() > data['start_time']:
            raise serializers.ValidationError('you cant start a tournament in the past!')

        if len(data['name']) >= 36:
            raise serializers.ValidationError('name is too long')

        return data

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.is_ongoing = validated_data.get('is_ongoing', instance.is_ongoing)
        instance.save()
        return instance

    def create(self, validated_data):
        created_at = datetime.now()

        tour = Tournaments.objects.create(
            name=validated_data['name'],
            created_at=created_at,
            start_time=validated_data['start_time'],
            type=validated_data['type'],
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


class PlayerStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerStats
        fields = ['participant', 'score', 'omw']
        validators = [
            UniqueTogetherValidator(
                queryset=PlayerStats.objects.all(),
                fields=['participant']
            )
        ]

    def update(self, instance, validated_data):
        instance.omw = validated_data.get('omw', instance.omw)
        instance.score = validated_data.get('score', instance.score)
        instance.save()
        return instance


class ParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participants
        fields = ['participant_id', 'game_username', 'username', 'user', 'tournament', 'checked_in']
        validators = [
            UniqueTogetherValidator(
                queryset=Participants.objects.all(),
                fields=['tournament', 'user']
            )
        ]

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.game_username = validated_data.get('game_username', instance.game_username)
        instance.checked_in = validated_data.get('checked_in', instance.checked_in)
        instance.save()
        return instance

    def can_register(self, tournament: Tournaments) -> None:
        if tournament.is_ongoing or tournament.end_time != None:  # TODO: add capacity check
            raise serializers.ValidationError("Cant register to tournament.")

    def create(self, validated_data):
        if 'tournament' in validated_data:
            self.can_register(validated_data['tournament'])

        if 'game_username' not in validated_data:
            raise serializers.ValidationError("Cant register without game username.")

        return Participants.objects.create(
            tournament=validated_data['tournament'],
            username=validated_data['username'], game_username=validated_data['game_username'],
            user=validated_data['user']
        )
