from django.contrib.auth.models import Group
from django.contrib.auth.models import User


def is_tournament_admin(user: User) -> bool:
    return user.groups.filter(name="tournament_admin").exists()

def is_tournament_organizer(user: User) -> bool:
    return user.groups.filter(name="tournament_organizer").exists()


