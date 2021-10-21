from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import request
from rest_framework import generics, viewsets,status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.decorators import action

from apps.pokerboard.models import Pokerboard, Invite, ManagerCredentials
from apps.pokerboard.serializer import (
    PokerBoardCreationSerializer, PokerBoardSerializer, InviteCreateSerializer,
    InviteSerializer, PokerboardUserSerializer, ManagerLoginSerializer
)
from apps.user.models import User
from apps.group.models import Group
from apps.pokerboard.permissions import CustomPermissions

from django.http import JsonResponse

class PokerBoardViewSet(viewsets.ModelViewSet):
    """
    Pokerboard View for CRUD operations
    """
    queryset = Pokerboard.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PokerBoardCreationSerializer
        return PokerBoardSerializer
    
    
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


    @action(detail=True, methods=['get','post', 'patch', 'delete'], permission_classes=[IsAuthenticated, CustomPermissions])
    def invite(self, request, pk=None):
        """
        /pokerboard/108/invite/ - manager - create invite
                                - user - accept invite
        Method to invite user/group to pokerboard
        Route: /pokerboard/{pk}/invite/ 
        Method : post - Create invitation
                 patch - Accept invite
        params : 
            Required : Either email or group_id
            Optional : role - 0/1
        """
        pokerboard_id = self.kwargs['pk']
        context = {
            'pokerboard': pokerboard_id,
            'method': request.method
        }
        if request.method in ['POST', 'DELETE']:
            users = []
            group_id = None

            serializer = InviteCreateSerializer(
                data=request.data, context=context)
            serializer.is_valid(raise_exception=True)

            if 'email' in request.data.keys():
                user = User.objects.get(email=request.data['email'])
                users.append(user)
            elif 'group_id' in request.data.keys():
                group_id = request.data['group_id']
                group = Group.objects.get(id=group_id)
                users = group.users.all()

        if request.method == 'POST':
            # TODO : Send mail for signup if doesnt exist
            for user in users:
                try:
                    invite = Invite.objects.get(user=user.id,pokerboard=pokerboard_id)
                    invite.status = 0
                    invite.save()
                except ObjectDoesNotExist:
                    serializer = InviteSerializer(
                        data={**request.data, 'pokerboard': pokerboard_id, 'user': user.id, 'group': group_id})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
            return Response({'msg': '{choice} successfully invited'.format(choice='Group' if group_id is not None else 'User')})

        if request.method == 'PATCH':
            user = request.user
            serializer = InviteCreateSerializer(
                data=request.data, context={**context, 'user': user})
            serializer.is_valid(raise_exception=True)
            invite = Invite.objects.get(
                user=user.id, pokerboard=pokerboard_id)
            if invite.user == None:
               pass
               #TODO: if comes through group
            else:
                user_data = {
                    "user": user.id,
                    "pokerboard": pokerboard_id
                }
                serializer = PokerboardUserSerializer(
                    data=user_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                invite.status = 1
                invite.save()

            return Response(data={'msg': 'Welcome to the pokerboard!'})

        if request.method == 'DELETE':
            for user in users:
                invite = Invite.objects.get(
                    user_id=user.id, pokerboard_id=pokerboard_id)
                invite.status = -1
            return Response(data={'msg': 'Invite successfully revoked.'})
    
class ManagerLoginView(generics.CreateAPIView):
    queryset = ManagerCredentials.objects.all()
    serializer_class = ManagerLoginSerializer
    permission_classes = [IsAuthenticated,]

    def perform_create(self, serializer):
        print("::: self user", self.request.user)
        serializer.save(user = self.request.user)
