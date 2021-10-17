from rest_framework import response, status, viewsets
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, DestroyAPIView


from .models import Group
from .permissions import IsGroupOwnerPermission
from apps.group import serializers as group_serializer 
from apps.user import models as user_models
from apps.group import models as group_models

class GroupViewSet(viewsets.ModelViewSet):
    queryset= Group.objects.all()
    serializer_class = group_serializer.GroupSerializer
    permission_classes = [IsGroupOwnerPermission]

    def perform_create(self, serializer):
        """
        Saves serializer and adds owner property as current user
        """
        serializer.save(owner=self.request.user)

class AddGroupMemberView(CreateAPIView):
    serializer_class = group_serializer.AddGroupMemberSerializer
    permission_classes = [IsGroupOwnerPermission]


class RemoveGroupMemberView(DestroyAPIView):
    serializer_class = group_serializer.RemoveGroupMemberSerializer
    permission_classes = [IsGroupOwnerPermission]

    def destroy(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group_id = serializer.data["group"]
        email = serializer.data["email"]
        user_instance = user_models.User.objects.get(email=email)
        group_instance = group_models.Group.objects.get(id=group_id)
        group_instance.members.remove(user_instance)
        return Response(data=serializer.data, status=status.HTTP_200_OK)