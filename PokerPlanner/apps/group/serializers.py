from rest_framework import serializers

from apps.group.models import Group

from apps.user.models import User
from apps.user.serializers import UserSerializer


class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True,required=False)
    class Meta:
        model = Group
        fields = ['id', 'owner', 'name', 'members']


class GroupUpdateSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField()

    class Meta:
        model = Group
        fields = ['id', 'owner', 'name', 'members']

    def validate_user_email(self, attrs):
        user = User.objects.filter(email=attrs)
        if not user.exists():
            raise serializers.ValidationError('Invalid user!')
        if self.instance.created_by == user[0]:
            raise serializers.ValidationError('Admin cannot join again!')
        if self.instance.users.filter(email=attrs).exists():
            raise serializers.ValidationError('Already a member!')
        return super().validate(attrs)

    def update(self, instance, validated_data):
        user = User.objects.get(email=validated_data['user_email'])
        instance.users.add(user)
        return super().update(instance, validated_data)
