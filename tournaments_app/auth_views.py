from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from tournaments_app.serializers import *


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


@api_view(['POST'])
def signup(request):
    s = SignupSerializer(data={
        "username": request.data['username'],
        "email": request.data['email'],
        "password": request.data['password'],
        "first_name": request.data['first_name'],
        "last_name": request.data['last_name']
    })
    print(s)
    s.is_valid(raise_exception=True)
    user = s.save()
    token = RefreshToken.for_user(user)
    return JsonResponse(data={"access": str(token.access_token),
                              "refresh": str(token), "username": user.username})


# @TODO: add organization fetching for the current user
# Get the organizations where organizer_id equals to the request.user.id
# or request.user is an admin for that organization
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request: Request):
    serializer = UserSerializer(instance=request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request: Request):
    users = User.objects.all()
    serializer = UserSerializer(instance=users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_staff(request: Request):
    requester: User = request.user
    userid = request.query_params["userid"]
    set_staff = request.query_params.get("staff", "True")
    if requester.is_superuser:
        user = get_object_or_404(User, id=userid)
        user.is_staff = set_staff.lower() != "false"
        user.save()
        return Response(status=200)
    else:
        return Response(status=400)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request: Request):
    user: User = request.user
    first_name = request.query_params.get("first-name", "")
    last_name = request.query_params.get("last-name", "")
    print(first_name, last_name)
    if first_name != "":
        user.first_name = first_name
    if last_name != "":
        user.last_name = last_name
    user.save()
    return Response(status=200)
