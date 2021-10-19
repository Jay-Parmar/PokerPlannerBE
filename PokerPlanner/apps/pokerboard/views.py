from django.http import request
from rest_framework import generics, viewsets,status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pokerboard.models import Pokerboard, ManagerCredentials
from apps.pokerboard.serializer import PokerBoardCreationSerializer, ManagerLoginSerializer


class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    queryset = Pokerboard.objects.all()
    serializer_class = PokerBoardCreationSerializer
    permission_classes = [IsAuthenticated]

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
    queryset = ManagerCredentials.objects.all()
    serializer_class = ManagerLoginSerializer
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        print("::: self user", self.request.user)
        serializer.save(user = self.request.user)
