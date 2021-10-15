from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import generics, permissions, request, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


from apps.user import (
    serializers as user_serializers,
    models as user_models
)
from .tasks import send_email_task

class UserViewSet(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = user_serializers.UserSerializer
    queryset = user_models.User.objects.all()

    def create(self, request, *args, **kwargs):
        '''Create a new User.'''
        serializer = self.get_serializer(data=request.data["user"])
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.create(user=user)
        verification_token = PasswordResetTokenGenerator().make_token(user)
        send_email_task.delay(user.first_name, user.pk, verification_token, user.email)
        return Response({**serializer.data, "token": token.key}, status=status.HTTP_200_OK)
    
    def get_object(self):
        return self.request.user
    

class ChangePasswordView(generics.UpdateAPIView):

    queryset = user_models.User.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = user_serializers.ChangePasswordSerializer


class Login(APIView):
    """
    View for Performing Login Verification
    """       
    serializer_class = user_serializers.LoginSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data["user"], context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        if 'user' not in serializer.validated_data:
            return Response({"NOT FOUND"})
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'id': user.pk,
            'email': user.email,
            'first_name' : user.first_name,
            'last_name' : user.last_name
        })


class Logout(ObtainAuthToken):
    """
    Logout method for logging out after session
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, format=None):
        '''Removes token from user when they log out.'''
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        return Response({"success": ("Successfully logged out.")}, status=status.HTTP_200_OK)

class ActivateAccountView(UpdateAPIView):
    serializer_class = user_serializers.VerifyAccountSerializer
    queryset = user_models.User.objects.all()
    permission_classes = [AllowAny]
