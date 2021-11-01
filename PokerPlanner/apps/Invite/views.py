from rest_framework import mixins, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.pokerboard import models as pokerboard_models
from apps.Invite import serializers as Invite_serializers
from apps.Invite import permissions 
from apps.pokerboard import constants 
from apps.pokerboard import serializer as pokerboard_serializers


class ManagerListInviteView(ListAPIView):
    """
    View for retrieving all invites sent by manager to uers
    """
    serializer_class = Invite_serializers.InviteSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        pokerboard_id = request.query_params.get('pokerboard')
        inivites = pokerboard_models.Invite.objects.filter(pokerboard=pokerboard_id)
        serializer = self.get_serializer(inivites, many=True)
        return Response(serializer.data)


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

    def perform_destroy(self, instance):
        instance.status = constants.DECLINED
        instance.save()
    
    def create_pokerboard_user(self, request):
        invite = self.get_object()
        user_data = {
            "user": request.user.id,
            "pokerboard": invite.pokerboard_id,
            'group': invite.group_id,
        }
        serializer = pokerboard_serializers.PokerboardUserSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return
    
    def partial_update(self, request, *args, **kwargs):
        invite = self.get_object()
        self.create_pokerboard_user(request)
        invite.status = constants.ACCEPTED
        invite.save()
        serializer = Invite_serializers.InviteSerializer(instance=invite)
        return Response(data={'Added to the pokerboard'})
