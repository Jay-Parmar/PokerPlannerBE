from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.forms import ValidationError

from rest_framework import serializers
from rest_framework.authtoken.models import Token

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
    class Meta:
        model = user_models.User
        fields = ['email', 'password']
    
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        """   
        Validating password and email 
        """
        user_queryset = get_user_model().objects.filter(email=data.get('email'))
        if not user_queryset:
            raise ValidationError(
                ("Invalid Credentials"),
                code='invalid'
            )
        if not check_password(data.get('password'), user_queryset[0].password):
            raise ValidationError(
                ('Invalid Credentials'),
                code='invalid',
            )
        else:
            data['user'] = get_user_model().objects.get(email=data.get('email'))
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = user_models.User
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
    
        instance.set_password(validated_data['password'])
        instance.save()
    
        return instance
    
    
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
