from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator

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


class LoginSerializer(UserSerializer):
    """
    Use Serializer for performing Login operations
    """
    email = serializers.EmailField()
    token = serializers.SerializerMethodField()
    
    class Meta(UserSerializer.Meta):
        model = user_models.User
        fields = UserSerializer.Meta.fields + ['token']
        extra_kwargs = {
            'first_name': {'read_only': True},
            'last_name': {'read_only': True},
            'password': {'write_only': True},
        }

    def get_token(self, instance):
        """
        Generate token on user login.
        """
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
        data['id'] = user.id
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
