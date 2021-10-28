from rest_framework import mixins, status, viewsets
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pokerboard import models as pokerboard_models
from apps.Invite import serializers as Invite_serializers
from apps.Invite import permissions 
from apps.pokerboard import constants 
from apps.pokerboard import serializer as pokerboard_serializers


class InviteViewSet(viewsets.ModelViewSet):
    """
    Invite View for CRUD operations
    """
    queryset = pokerboard_models.Invite.objects.all()
    serializer_class = Invite_serializers.InviteSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [IsAuthenticated, permissions.CustomPermissions]
        else:
            self.permission_classes = [IsAuthenticated]
        return super(InviteViewSet, self).get_permissions()
    
    def get_queryset(self):
        return pokerboard_models.Invite.objects.filter(user_id=self.request.user.id, status=constants.PENDING)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return Invite_serializers.InviteCreateSerializer
        return super().get_serializer_class()

    def partial_update(self, request, *args, **kwargs):
        invite = self.get_object()
        user_data = {
            "user": request.user.id,
            "pokerboard": invite.pokerboard_id,
            'group': invite.group_id,
        }
        serializer = pokerboard_serializers.PokerboardUserSerializer(
            data=user_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        invite.status = constants.ACCEPTED
        invite.save()
        serializer = Invite_serializers.InviteSerializer(instance=invite)
        # return Response(data=serializer.data)
        return Response(data={'msg': 'Welcome to the pokerboard!'})
    
    def perform_destroy(self, instance):
        if instance.status != constants.PENDING:
            return Response(data={'msg' : 'Already accepted'},status=status.HTTP_400_BAD_REQUEST)
        instance.status = constants.DECLINED
        instance.save()


class ManagerListInviteView(ListAPIView):
    """
    View for retrieving all invites sent by manager to uers
    """
    serializer_class = Invite_serializers.InviteSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        inivites = pokerboard_models.Invite.objects.filter(pokerboard=request.data['pokerboard'])
        serializer = self.get_serializer(inivites, many=True)
        return Response(serializer.data)
    