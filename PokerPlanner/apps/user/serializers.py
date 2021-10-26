from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from apps.user import models as user_models
from .verificationToken import account_activation_token


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
    first_name = serializers.CharField(max_length=128, read_only=True)
    last_name = serializers.CharField(max_length=128, read_only=True)
    token = serializers.SerializerMethodField()
    
    class Meta:
        model = user_models.User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'token']

    def get_token(self, instance):
        user = user_models.User.objects.get(email=instance['email'])
        token, _ = Token.objects.get_or_create(user=user)
        return token.key

    def validate(self, data):
        """   
        Validating password and email
        """
        email = data.get('email', None)
        password = data.get('password', None)

        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                ("Invalid Credentials"),
                code='invalid'
            )

        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = user_models.User
        fields = ['old_password', 'password']

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
    """
    Activate account email verification serializer
    """
    token = serializers.CharField(max_length=150, write_only=True)

    def validate_token(self, value):
        """
        Checks if the token is valid
        """
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
