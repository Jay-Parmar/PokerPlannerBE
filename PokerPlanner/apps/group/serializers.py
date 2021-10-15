from django.db.models import fields

from rest_framework import request, serializers

from apps.group import models as group_models
from apps.user import (serializers as user_serializers,
models as user_model)

class GroupSerializer(serializers.ModelSerializer):
    """
    Serializer for Creating Group.
    """
    members = user_serializers.UserSerializer(many=True, read_only=True)
    class Meta:
        model = group_models.Group
        fields = ['name', 'owner', 'members']
    
    def create(self, validated_data):
        request = self.context.get('request').data
        users = request['members']
        createdby = user_model.User.objects.get(id=request['owner'])
        group = group_models.Group.objects.create(name=validated_data['name'], owner=createdby)
        for user in users:
            group_member = user_model.User.objects.get(id=user['id'])
            group.members.add(group_member)
        return group
