from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.group import models as group_models
from apps.group import serializers as group_serializer
from apps.user import models as user_models

from apps.group.permissions import IsGroupOwnerPermission, IsGroupOwnerOrMember


class GroupViewSet(viewsets.ModelViewSet):
    """
    Group API for creating group and get list of groups a user is associated with.
    """
    serializer_class = group_serializer.GroupSerializer
    permission_classes = [IsGroupOwnerPermission]


    def get_permissions(self):
        print(self.action)
        if self.action == 'retrieve':
            self.permission_classes = [IsGroupOwnerOrMember]
        else:
            self.permission_classes = [IsGroupOwnerPermission]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        Gets groups list in which current user is a member.
        """
        return group_models.Group.objects.filter(Q(members=self.request.user) | Q(owner=self.request.user)).distinct()


    def perform_create(self, serializer):
        """
        Saves serializer and adds owner property as current user
        """
        serializer.save(owner=self.request.user)


class GroupAddMemberView(CreateAPIView):
    """
    Group user API for adding and removing group member
    """
    serializer_class = group_serializer.AddGroupMemberSerializer
    permission_classes = [IsGroupOwnerPermission]


class GroupDeleteMemberView(viewsets.GenericViewSet, mixins.DestroyModelMixin):
    """
    View to remove user from a group.
    """
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        group = get_object_or_404(group_models.Group, id=self.kwargs['group_id'])
        return group.members.all()

    def destroy(self, request, *args, **kwargs):
        group = group_models.Group.objects.get(id=self.kwargs['group_id'])
        user = self.get_object()
        serializer = group_serializer.RemoveGroupMemberSerializer(
            data={"user": user.id}, context={'group': group}
        )
        serializer.is_valid(raise_exception=True)
        group.members.remove(user)
        return Response(status=status.HTTP_204_NO_CONTENT)
