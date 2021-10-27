from django.core.exceptions import ObjectDoesNotExist

from rest_framework import generics, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.group.models import Group
from apps.pokerboard import models as pokerboard_models
from apps.pokerboard import permissions as pokerboard_permissions
from apps.pokerboard import serializer as pokerboard_serializer
from apps.user import models as user_models


class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    queryset = pokerboard_models.Pokerboard.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return pokerboard_serializer.PokerBoardCreationSerializer
        return pokerboard_serializer.PokerBoardSerializer
    
    
    def create(self, request, *args, **kwargs):
        """
        Create new pokerboard
        Required : Token in header, Title, Description
        Optional : Estimate_type
        """
        request.data['manager_id'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

 
class ManagerLoginView(generics.CreateAPIView):
    queryset = pokerboard_models.ManagerCredentials.objects.all()
    serializer_class = pokerboard_serializer.ManagerLoginSerializer
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        serializer.save(user = self.request.user)
