from django.urls.conf import path
from rest_framework import generics, viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.pokerboard import models as pokerboard_models
from apps.pokerboard import serializer as pokerboard_serializers

from atlassian import Jira

class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    queryset = pokerboard_models.Pokerboard.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':  #self action
            return pokerboard_serializers.PokerBoardCreationSerializer
        return pokerboard_serializers.PokerBoardSerializer
    
    def get_queryset(self):
        return pokerboard_models.Pokerboard.objects.filter(manager=self.request.user)

    def create(self, request, *args, **kwargs):  #context use of
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


class ManagerLoginView(generics.ListCreateAPIView, generics.UpdateAPIView):
    """
    Create a manager entry if the credentials are valid.
    """
    queryset = pokerboard_models.ManagerCredentials.objects.all()
    permission_classes = [IsAuthenticated,]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return pokerboard_serializers.ManagerLoginSerializer
        return pokerboard_serializers.ManagerDetailSerializer

    def get_queryset(self):  #post(create) me queryset ki zarurt nai hoti
        return pokerboard_models.ManagerCredentials.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = pokerboard_models.ManagerCredentials.objects.get(user=self.request.user)
        print("instance:::", instance.data)
        serializer = self.get_serializer(instance)
        print("Seria:::", serializer)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    # def patch(self, request):
    #     print(":::req", request)
    #     testmodel_object = pokerboard_models.ManagerCredentials.objects.get(user=self.request.user)
    #     serializer = pokerboard_serializers.ManagerDetailSerializer(testmodel_object, 
    #                  data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        # user_data = {
        #     "password": request.password,
        #     "url": instance.url,
        #     "username": instance.username,
        # }
        # serializer = pokerboard_serializers.ManagerDetailSerializer(data=user_data)
        # serializer.is_valid(raise_exception=True)
        # serializer.save()
        instance.password = request.password
        instance.save()
        return Response(data={"message": "successfully updated"}, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        try:
            serializer.save(user=self.request.user)
        except Exception as err:
            return Response(data={'msg': 'User already present'}, status=status.HTTP_200_OK)
            # return self.partial_update(self.request)


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


class CommentView(generics.CreateAPIView):
    """
    Comment View to comment on a JIRA ticket
    """
    serializer_class = pokerboard_serializers.CommentSerializer
    queryset = pokerboard_models.ManagerCredentials.objects.all()
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        """
        Create a comment on Jira.
        """
        manager = pokerboard_models.ManagerCredentials.objects.get(user=self.request.user)
        jira = Jira(
            url = manager.url,
            username = manager.username,
            password = manager.password,
        )
        jira.issue_add_comment(serializer.validated_data['ticket_id'], serializer.validated_data['comment'])


class TicketDetailView(generics.RetrieveAPIView):
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
