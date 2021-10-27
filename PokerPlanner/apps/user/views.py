from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import generics, permissions, status, viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.user import (
    serializers as user_serializers,
    models as user_models
)
from .tasks import send_email_task
from apps.pokerboard.models import Invite
from apps.pokerboard.serializer import InviteSerializer


class UserViewSet(generics.RetrieveUpdateDestroyAPIView, generics.CreateAPIView):
    """
    A viewset for viewing and editing user instances.
    """
    serializer_class = user_serializers.UserSerializer
    queryset = user_models.User.objects.all()
    permission_classes = [permissions.AllowAny,]

    def create(self, request, *args, **kwargs):
        '''Create a new User.'''
        serializer = self.get_serializer(data=request.data.get('user'))
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        verification_token = PasswordResetTokenGenerator().make_token(user)
        send_email_task.delay(user.first_name, user.pk, verification_token, user.email)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    
    def get_object(self):
        return self.request.user


class ListInvite(viewsets.ModelViewSet):
    """
    List Invite to list a users invite
    """
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'delete']
    
    def get_queryset(self):
        return Invite.objects.filter(user_id=self.request.user.id, is_accepted=False)
    

class ChangePasswordView(generics.UpdateAPIView):

    queryset = user_models.User.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = user_serializers.ChangePasswordSerializer

    def get_object(self):
        return self.request.user


class LoginView(APIView):
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


class LogoutView(APIView):
    """
    Logout method for logging out after session
    """
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request, format=None):
        '''Removes token from user when they log out.'''
        try:
            request.user.auth_token.delete()
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)


class ActivateAccountView(generics.UpdateAPIView):
    serializer_class = user_serializers.VerifyAccountSerializer
    queryset = user_models.User.objects.all()
    permission_classes = [permissions.AllowAny]
