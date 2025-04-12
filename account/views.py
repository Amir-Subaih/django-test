from django.shortcuts import render, get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import status
from .serializers import SingUpSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from django.utils.crypto import get_random_string

from datetime import datetime, timedelta
from django.core.mail import send_mail

# from .models import Profile


# Create your views here.


@api_view(['POST'])
def register(request):
    data = request.data
    user = SingUpSerializer(data=data)
    if user.is_valid():
        if not User.objects.filter(email=data['email']).exists():
            user = User.objects.create(
                                        username=data['username'],
                                        email=data['email'], 
                                        password=make_password(data['password'])
                                        )
            # Create the Profile instance with user_type
            # Profile.objects.create(
            #     user=user,
            #     user_type=data.get('user_type', 'user')  # default to 'user' if not provided
            # )
            return Response({'message': 'success'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
        
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
    user.username = data['username']
    user.email = data['email']
    user.save()
    serializer = UserSerializer(user, many=False)
    return Response({'message': 'Profile Updated','data':serializer.data}, status=status.HTTP_200_OK)


def get_current_host(request):
    protocol = request.is_secure() and 'https' or 'http'
    host = request.get_host()
    return "{protocol}://{host}/".format(protocol=protocol, host=host)


@api_view(['POST'])
def forgot_password(request):
    data = request.data
    user = get_object_or_404(User, email=data['email'])
    token = get_random_string(40)
    exprire_data = datetime.now() + timedelta(minutes=30)
    user.profile.reset_password_token = token
    user.profile.reset_password_expire = exprire_data
    user.profile.save()
    host = get_current_host(request)
    link = "http://127.0.0.1:8000/api/account/resetPassword/{token}".format(token=token) #"{host}api/reset_password/token".format(host=host)
    body = "Your reset password link is {link}".format(link=link)
    send_mail(
        "Reset Password from AMS",
        body,
        "ams2002@gmail.com",
        [data['email']]
    )
    return Response({'message': 'Password reset sent to{email}'.format(email=data['email'])}, status=status.HTTP_200_OK)

@api_view(['POST'])
def reset_password(request, token):
    data = request.data
    user = get_object_or_404(User, profile__reset_password_token=token)
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
