from rest_framework import serializers
from account.models import Account
from django.contrib.auth.hashers import make_password  # Add this import

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class SingUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('username', 'email', 'password', 'user_type')

        extra_kwargs = {
            'password': {'required': True, 'allow_blank': False, 'min_length': 8},
            'email': {'required': True, 'allow_blank': False},
            'username': {'required': True, 'allow_blank': False},
            'user_type': {'required': True}
        }

    def create(self, validated_data):
        # Hash the password before saving
        account = Account(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(validated_data['password']),  # This will now work
            user_type=validated_data['user_type']
        )
        account.save()
        return account

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'username', 'email', 'user_type')
# account/serializers.py

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['user_id'] = user.id  # Directly use user.id instead of user.account.id
        token['user_type'] = user.user_type
        token['isAdmin'] = user.isAdmin

        return token
