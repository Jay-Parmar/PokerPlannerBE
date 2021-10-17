from django.db.models.query_utils import InvalidQuery
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.user import (
    serializers as user_serializers,
    models as user_models
)
from .tasks import send_email_task

class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = user_serializers.UserSerializer
    queryset = user_models.User.objects.all()
    permission_classes = [permissions.AllowAny,]

    def create(self, request, *args, **kwargs):
        """
        Create a new User.
        """
        serializer = self.get_serializer(data=request.data.get('user', {}))
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.get(user=user)
        verification_token = PasswordResetTokenGenerator().make_token(user)
        send_email_task.delay(user.first_name, user.pk, verification_token, user.email)
        return Response({**serializer.data, "token": token.key}, status=status.HTTP_200_OK)


class Login(APIView):
    """
    View for Performing Login Verification
    """
    serializer_class = user_serializers.LoginSerializer
    renderer_classes = [JSONRenderer]
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data.get('user', {}))
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class Logout(ObtainAuthToken):
    """
    Logout method for logging out after session
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def get(self, request, format=None):
        '''Removes token from user when they log out.'''
        try:
            request.user.auth_token.delete()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)


class ActivateAccountView(UpdateAPIView):
    serializer_class = user_serializers.VerifyAccountSerializer
    queryset = user_models.User.objects.all()
    permission_classes = [AllowAny]
