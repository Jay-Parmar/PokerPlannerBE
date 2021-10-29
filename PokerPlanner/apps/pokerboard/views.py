from rest_framework import generics, viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.pokerboard import models as pokerboard_models
from apps.pokerboard import serializer as pokerboard_serializers


class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    queryset = pokerboard_models.Pokerboard.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return pokerboard_serializers.PokerBoardCreationSerializer
        return pokerboard_serializers.PokerBoardSerializer
    
    def get_queryset(self):
        return pokerboard_models.Pokerboard.objects.filter(manager=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create new pokerboard
        Required : Token in header, Title, Description
        Optional : Estimate_type
        """
        serializer = self.get_serializer(
            data={**request.data, 'manager_id': request.user.id}
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ManagerLoginView(generics.CreateAPIView):
    """
    Create a manager entry if the credentials are valid.
    """
    queryset = pokerboard_models.ManagerCredentials.objects.all()
    serializer_class = pokerboard_serializers.ManagerLoginSerializer
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        try:
            serializer.save(user = self.request.user)
        except Exception as err:
            raise serializers.ValidationError("Credentials already present")


class PokerboardMembersView(viewsets.ModelViewSet):
    """
    Pokerboard member API View for listing and removing user/groups
    """
    queryset = pokerboard_models.PokerboardUser.objects.all()
    serializer_class = pokerboard_serializers.PokerboardMemberSerializer
    permission_classes = [IsAuthenticated,]

    def retrieve(self, request, pk = None):
        """
        Gets all the pokerboard's members
        """
        group_members = pokerboard_models.PokerboardUser.objects.filter(pokerboard=pk)
        members = self.serializer_class(group_members, many=True)
        return Response(members.data)
    
        
class VoteViewSet(viewsets.ModelViewSet):
    """
    PokerBoard Vote view for CRUD operation
    """
    queryset = pokerboard_models.UserTicketEstimate.objects.all()
    serializer_class = pokerboard_serializers.VoteSerializer
    permission_classes = [IsAuthenticated]


class TicketViewSet(viewsets.ModelViewSet):
    """
    Ticket view to get/update/delete ticket
    """
    queryset = pokerboard_models.Ticket.objects.all()
    serializer_class = pokerboard_serializers.PokerboardTicketSerializer
    permission_classes = [IsAuthenticated]


class CommentView(generics.CreateAPIView, generics.ListAPIView):
    """
    Comment View to comment on a JIRA ticket
    """
    serializer_class = pokerboard_serializers.CommentSerializer
    permission_classes = [IsAuthenticated]
