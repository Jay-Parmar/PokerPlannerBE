from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import serializers

from apps.user import models as user_models


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Registration.
    """
    token = serializers.CharField(max_length=255, read_only=True)
    class Meta:
        model = user_models.User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'token']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        user = user_models.User.objects.create(**validated_data)
        return {
            'email': user.email,
            'token': user.token,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'id': user.id
        }


class LoginSerializer(serializers.Serializer):
    """
    Use Serializer for performing Login operations
    """
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, write_only=True)
    first_name = serializers.CharField(max_length=128, read_only=True)
    last_name = serializers.CharField(max_length=128, read_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    
    def validate(self, data):
        """   
        Validating password and email
        """
        email = data.get('email', None)
        password = data.get('password', None)
        if email is None or password is None:
            raise serializers.ValidationError("Email and password required.")
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                ("Invalid Credentials"),
                code='invalid'
            )

        return {
            'email': user.email,
            'token': user.token,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'id': user.id
        }


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
