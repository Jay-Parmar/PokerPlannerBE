from django.db.models.query_utils import Q
from rest_framework import status, viewsets
from rest_framework.generics import CreateAPIView, DestroyAPIView
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


class GroupMemberView(CreateAPIView, DestroyAPIView):
    """
    Group user API for adding and removing group member
    """
    serializer_class = group_serializer.AddGroupMemberSerializer
    permission_classes = [IsGroupOwnerPermission]

    def destroy(self, request, *args, **kwargs):
        """
        Removes a member from a group
        """
        serializer = group_serializer.RemoveGroupMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group_id = serializer.data["group"]
        email = serializer.data["email"]
        user_instance = user_models.User.objects.get(email=email)
        group_instance = group_models.Group.objects.get(id=group_id)
        group_instance.members.remove(user_instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)



