from django.db.models.query_utils import InvalidQuery
from rest_framework import permissions, status
from rest_framework import viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.user import (
    serializers as user_serializers,
    models as user_models
)


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
        serializer = self.get_serializer(data=request.data["user"])
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.get(user=user)
        return Response({**serializer.data, "token": token.key}, status=status.HTTP_201_CREATED)


class Login(APIView):
    """
    View for Performing Login Verification
    """       
    serializer_class = user_serializers.LoginSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data.get('user', {}))
        serializer.is_valid(raise_exception=True)
        user = user_models.User.objects.get(email=serializer.data.get('email'))
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'id': user.pk,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
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
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)
