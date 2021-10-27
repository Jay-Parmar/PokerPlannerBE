from rest_framework import generics, viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.group import models as group_models
from apps.pokerboard import models as pokerboard_models
from apps.pokerboard import serializer as pokerboard_serializers
from apps.pokerboard import permissions as pokerboard_permissions
from apps.user import models as user_models


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

    @action(detail=True, methods=['get','post', 'patch', 'delete'], permission_classes=[IsAuthenticated, pokerboard_permissions.CustomPermissions])
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

            serializer = pokerboard_serializers.InviteCreateSerializer(
                data=request.data, context=context)
            serializer.is_valid(raise_exception=True)

            if 'email' in request.data.keys():
                user = user_models.User.objects.get(email=request.data['email'])
                users.append(user)
            elif 'group_id' in request.data.keys():
                group_id = request.data['group_id']
                group = group_models.Group.objects.get(id=group_id)
                users = group.users.all()

        if request.method == 'POST':
            # TODO : Send mail for signup if doesnt exist
            for user in users:
                serializer = pokerboard_serializers.InviteSerializer(
                    data={**request.data, 'pokerboard': pokerboard_id, 'user': user.id, 'group': group_id})
                serializer.is_valid(raise_exception=True)
                serializer.save()
            return Response({'msg': '{choice} successfully invited'.format(choice='Group' if group_id is not None else 'User')})

        if request.method == 'PATCH':
            user = request.user
            serializer = pokerboard_serializers.InviteCreateSerializer(
                data=request.data, context={**context, 'user': user})
            serializer.is_valid(raise_exception=True)
            invite = pokerboard_models.Invite.objects.get(
                user=user.id, pokerboard=pokerboard_id)
            if invite.user == None:
               pass
               #TODO: if comes through group
            else:
                user_data = {
                    "user": user.id,
                    "pokerboard": pokerboard_id
                }
                serializer = pokerboard_serializers.PokerboardUserSerializer(
                    data=user_data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                invite.is_accepted = True
                invite.save()

            return Response(data={'msg': 'Welcome to the pokerboard!'})

        if request.method == 'DELETE':
            for user in users:
                invite = pokerboard_models.Invite.objects.get(
                    user_id=user.id, pokerboard_id=pokerboard_id)
                invite.delete()
            return Response(data={'msg': 'Invite successfully revoked.'})


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
