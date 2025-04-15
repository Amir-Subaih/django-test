from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Account
from django.contrib.auth.hashers import make_password
from rest_framework import status
from .serializers import SingUpSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.core.mail import send_mail

@api_view(['POST'])
def register(request):
    data = request.data
    serializer = SingUpSerializer(data=data)
    if serializer.is_valid():
        if not Account.objects.filter(email=data['email']).exists():
            account = serializer.save()
            return Response({'message': 'success'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def currentUser(request):
    user = UserSerializer(request.user, many=False)
    return Response(user.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateProfile(request):
    user = request.user
    data = request.data
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.save()
    serializer = UserSerializer(user, many=False)
    return Response({'message': 'Profile Updated', 'data': serializer.data}, status=status.HTTP_200_OK)

def get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/".format(protocol=protocol, host=host)

@api_view(['POST'])
def forgot_password(request):
    data = request.data
    user = get_object_or_404(Account, email=data['email'])  # Use Account instead of User
    token = get_random_string(40)
    expire_data = datetime.now() + timedelta(minutes=30)
    user.profile.reset_password_token = token
    user.profile.reset_password_expire = expire_data
    user.profile.save()
    host = get_current_host(request)
    link = "http://127.0.0.1:8000/api/account/resetPassword/{token}".format(token=token)
    body = "Your reset password link is {link}".format(link=link)
    send_mail(
        "Reset Password from AMS",
        body,
        "ams2002@gmail.com",
        [data['email']]
    )
    return Response({'message': 'Password reset sent to {email}'.format(email=data['email'])}, status=status.HTTP_200_OK)

@api_view(['POST'])
def reset_password(request, token):
    data = request.data
    user = get_object_or_404(Account, profile__reset_password_token=token)  # Use Account instead of User
    if user.profile.reset_password_expire.replace(tzinfo=None) < datetime.now():
        return Response({'message': 'Token Expired'}, status=status.HTTP_400_BAD_REQUEST)
    if data['password'] != data['confirm_password']:
        return Response({'message': 'Password does not match'}, status=status.HTTP_400_BAD_REQUEST)
    user.password = make_password(data['password'])
    user.profile.reset_password_token = ""
    user.profile.reset_password_expire = None
    user.profile.save()
    user.save()
    return Response({'message': 'Password Reset Successfully'}, status=status.HTTP_200_OK)
