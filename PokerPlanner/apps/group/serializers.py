from rest_framework import serializers

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
        fields = ['id', 'name', 'owner', 'members', 'created_at']
        extra_kwargs = {
            'owner': {
                'read_only': True,
            },
        }


class AddGroupMemberSerializer(serializers.Serializer):
    """
    Serializer for adding member to a group
    """
    email = serializers.EmailField(write_only=True)
    user = user_serializers.UserSerializer(read_only=True)    
    group = serializers.IntegerField()
    
    def validate(self, data):
        """
        Checks if user with given email exists or not.
        If exists, check if the user has already been added to the group.
        """
        email = data["email"]
        group_id = data["group"]

        user = user_model.User.objects.filter(email=email)
        if not user.exists():
            raise serializers.ValidationError("No such user")
        
        group = group_models.Group.objects.filter(id=group_id)
        if not group.exists():
            raise serializers.ValidationError("Group not found")
        
        if group.first().members.filter(email=email).exists():
            raise serializers.ValidationError("A member can't be added to a group twice")
        return data

    def create(self, validated_data):
        """
        Adds user to a group
        """
        group_id = validated_data["group"]
        email = validated_data["email"]
        user_instance = user_model.User.objects.get(email=email)
        group_instance = group_models.Group.objects.get(id=group_id)
        group_instance.members.add(user_instance)
        return validated_data

class RemoveGroupMemberSerializer(serializers.Serializer):
    """
    Serializer for adding member to a group
    """
    email = serializers.EmailField()
    user = user_serializers.UserSerializer(read_only=True)    
    group = serializers.IntegerField()
    
    def validate(self, data):
        """
        Checks if user with given email exists or not.
        """
        email = data["email"]
        group_id = data["group"]

        user = user_model.User.objects.filter(email=email)
        if not user.exists():
            raise serializers.ValidationError("No such user")
        
        group = group_models.Group.objects.filter(id=group_id)
        if not group.exists():
            raise serializers.ValidationError("Group not found")

        if not group.first().members.filter(email=email).exists():
            raise serializers.ValidationError("User does not exists in the group")
    
        return data