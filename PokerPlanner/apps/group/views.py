from rest_framework import viewsets

from apps.group.models import Group
from apps.group.serializers import GroupSerializer, GroupUpdateSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    Group View for Performing CRUD operations.
    """
    serializer_class = GroupSerializer
    queryset = Group.objects.all()

    def get_serializer_class(self, *args, **kwargs):
        method = self.request.method
        if method == 'PATCH':
            return GroupUpdateSerializer
        return super().get_serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        request.data['owner'] = request.user.id
        return super().create(request, *args, **kwargs)
