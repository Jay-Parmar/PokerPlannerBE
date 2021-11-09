from django.contrib.postgres import fields
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.models.query_utils import Q
from django.http import request
from rest_framework import generics, mixins, viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.pokerboard import models as pokerboard_models
from apps.pokerboard import serializer as pokerboard_serializers


class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return pokerboard_serializers.PokerBoardCreationSerializer
        return pokerboard_serializers.PokerBoardSerializer
    
    def get_queryset(self):
        user = pokerboard_models.Pokerboard.objects.filter(Q(manager=self.request.user) |
                             Q(invites__user=self.request.user, invites__status=1)).distinct()
        return user

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["manager_id"] = self.request.user.id
        return context
    

class ManagerCreateView(generics.CreateAPIView):
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


class ManagerUpdateCredentialsView(generics.UpdateAPIView):
    """
    Create a manager entry if the credentials are valid.
    """
    queryset = pokerboard_models.ManagerCredentials.objects.all()
    serializer_class = pokerboard_serializers.ManagerLoginSerializer
    permission_classes = [IsAuthenticated,]

    def partial_update(self, serializer):
        try:
            serializer = self.get_serializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            credentials = pokerboard_models.ManagerCredentials.objects.get(user=self.request.user.id)
            credentials.url = self.request.data['url']
            credentials.username = self.request.data['username']
            credentials.password = self.request.data['password']
            credentials.save()
        except ObjectDoesNotExist:
            raise ValidationError("No such user found")
        return Response("update successfull")

class ManagerListCredentialView(generics.ListAPIView):
    """
    View for retrieving all invites sent by manager to uers
    """
    serializer_class = pokerboard_serializers.ManagerCredentialSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        credentials = pokerboard_models.ManagerCredentials.objects.filter(user=user_id)
        if credentials.first():
            serializer = self.get_serializer(credentials, many=True)
            return Response(serializer.data)
        else:
            return Response("No such Credentials found", status=status.HTTP_400_BAD_REQUEST)


class PokerboardMembersView(mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
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
    