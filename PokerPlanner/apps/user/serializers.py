from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.forms import ValidationError

from rest_framework import serializers, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from apps.user import models as user_models


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Registration.
    """
    class Meta:
        model = user_models.User
        fields = ['id', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True},
        }


class LoginSerializer(serializers.Serializer):
    """
    Use Serializer for performing Login operations
    """
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = user_models.User
        fields = ['email', 'password']
    
    def validate(self, data):
        """   
        Validating password and email
        """
        print("ijesiuci", data)
        email = data.get('email', None)
        password = data.get('password', None)
        print("email: ", email)
        print("pass: ", password)
        if email is None or password is None:
            raise serializers.ValidationError("Email and password required.")
        user = authenticate(email=email, password=password)
        print("::: after authenticate, user :: ", user)
        if user is None:
            raise serializers.ValidationError(
                ("Invalid Credentials"),
                code='invalid'
            )

        print("::: firstname ", user.first_name)
        data['user'] = user
        return data

class VerifyAccountSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=150, write_only=True)

    def validate_token(self, value):
        """
        Checks if the token is valid
        """
        account_activation_token = PasswordResetTokenGenerator()
        if account_activation_token.check_token(self.instance, value):
            return value
        raise serializers.ValidationError("Email Not Valid")

    def update(self, user, validated_data):
        """
        Activates user's account
        """
        user.is_verified = True
        user.save()
        return user
