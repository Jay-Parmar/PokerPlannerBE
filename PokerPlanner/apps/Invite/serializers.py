from rest_framework import serializers

from apps.group import models as group_models
from apps.pokerboard import models as pokerboard_models
from apps.pokerboard import constants
from apps.user import tasks as user_tasks
from apps.user import models as user_models


class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = pokerboard_models.Invite
        fields = '__all__'
        extra_kwargs = {
            'status': {'read_only': True}
        }

    def to_representation(self, instance):
        representation = super(InviteSerializer, self).to_representation(instance)
        representation['pokerboard_title'] = instance.pokerboard.title
        return representation
    
    def validate(self, attrs):
        invite = attrs['invite_id']
        if invite.status == constants.DECLINED:
            raise serializers.ValidationError('Invite doesnt exist!')
        if invite.status == constants.ACCEPTED:
            raise serializers.ValidationError('Invite already accepted!')
        return super().validate(attrs)
     

class InviteCreateSerializer(serializers.Serializer):
    pokerboard = serializers.PrimaryKeyRelatedField(
        queryset=pokerboard_models.Pokerboard.objects.all()
    )
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=group_models.Group.objects.all(), required=False
    )
    email = serializers.EmailField(required=False)
    user_role = serializers.ChoiceField(
        choices=constants.ROLE_CHOICES, required=False)
    
    def create(self, attrs):
        pokerboard = attrs['pokerboard']
        users = []
        if 'group_id' in attrs.keys():
            group = attrs['group_id']
            users = group.members.all()

        elif 'email' in attrs.keys():
            try:
                user = user_models.User.objects.get(email=attrs['email'])
                users.append(user)
            except user_models.User.DoesNotExist as e:
                user_tasks.send_invite_task.delay(attrs['email'])
                raise serializers.ValidationError("Email to signup in pokerplanner has been sent.Please check your email.")
        else:
            raise serializers.ValidationError('Provide group_id/email!')

        if 'email' in attrs.keys():
            for user in users:
                invite = pokerboard_models.Invite.objects.filter(
                    user=user.id, pokerboard=pokerboard.id
                )
                if pokerboard.manager == user:
                    raise serializers.ValidationError('Manager cannot be invited!')
                if invite.exists():
                    if invite[0].status == constants.ACCEPTED:
                        raise serializers.ValidationError('Already part of pokerboard')
                    elif invite[0].status == constants.PENDING:
                        raise serializers.ValidationError('Invite already sent!')

        existing_players = []
        invited_players = []
        for user in users:
            # invite = Invite.objects.update_or_create( pokerboard_id = pokerboard.id, user_id = user.id, defaults={'status' : constants.PENDING,'user_role' : role})
            poke_user = pokerboard_models.PokerboardUser.objects.filter(user=user,pokerboard=pokerboard.id)
            if not poke_user.exists() and pokerboard.manager != user:
                try:
                    invite = pokerboard_models.Invite.objects.get(pokerboard_id = pokerboard.id, user_id = user.id)
                    invite.status = constants.PENDING
                    if 'user_role' in attrs.keys():
                        invite.user_role = attrs['user_role']
                    invite.save()
                except pokerboard_models.Invite.DoesNotExist:
                    new_data = {
                        'pokerboard_id' : pokerboard.id,
                        'user_id' : user.id,
                        'email': user.email
                    }
                    if 'user_role' in attrs.keys():
                        new_data['user_role'] = attrs['user_role']
                    if 'group_id' in attrs.keys():
                        new_data['group'] = attrs['group_id']
                    invite = pokerboard_models.Invite.objects.create(**new_data)
                invited_players.append(user.email)
            else:
                existing_players.append(user.email)
        return invite
