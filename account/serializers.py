from rest_framework import serializers
from django.contrib.auth.models import User


class SingUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email','password')

        extra_kwargs = {
            'password': {'required': True ,'allow_blank':False,'min_length': 8},
            'email':{'required':True ,'allow_blank':False},
            'username': {'required': True ,'allow_blank':False},
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username', 'email')
