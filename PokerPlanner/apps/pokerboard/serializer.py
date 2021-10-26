from rest_framework import serializers, status

from apps.pokerboard import models as pokerboard_models
from apps.group.models import Group
from apps.user.models import User
from apps.user.serializers import UserSerializer
from apps.pokerboard import constants

from atlassian import Jira

import requests


class TicketsSerializer(serializers.ListSerializer):
    child = serializers.CharField()


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = pokerboard_models.Ticket
        fields = ['pokerboard', 'ticket_id', 'order', 'status']


class PokerBoardSerializer(serializers.ModelSerializer):
    manager = UserSerializer()
    ticket = TicketSerializer(source='tickets', many=True)

    class Meta:
        model = pokerboard_models.Pokerboard
        fields = ['id', 'manager', 'title', 'description',
                  'estimate_type', 'ticket']


class ManagerLoginSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = pokerboard_models.ManagerCredentials
        fields = ['url', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }


class PokerBoardCreationSerializer(serializers.ModelSerializer):
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())
    sprint_id = serializers.CharField(required=False, write_only=True)
    tickets = TicketsSerializer(required=False, write_only=True)
    jql = serializers.CharField(required=False, write_only=True)
    ticket_responses = serializers.SerializerMethodField()

    class Meta:
        model = pokerboard_models.Pokerboard
        fields = [
            'manager_id', 'title', 'description', 'tickets', 'sprint_id',
            'ticket_responses', 'jql'
        ]

    def get_ticket_responses(self, instance):
        user_obj = list(instance.items())[0][-1]
        manager = pokerboard_models.ManagerCredentials.objects.get(user=user_obj)
        jira = Jira(
            url = manager.url,
            username = manager.username,
            password = manager.password,
        )
        data = dict(instance)
        ticket_responses = []
        i = 0
        myJql = ""

        # If sprint, then fetch all tickets in sprint and add
        if 'sprint_id' in data:
            myJql = "Sprint = " + data['sprint_id']

        # Adding tickets
        if 'tickets' in data.keys():
            tickets = data['tickets']
            serializer = TicketsSerializer(data=tickets)
            serializer.is_valid(raise_exception=True)

            if(len(myJql) != 0):
                myJql += " OR "
            myJql += "issueKey in ("
            for ticket in tickets:
                myJql = myJql + ticket + ','
            myJql = myJql[:-1] + ')'

        # Adding jql
        if 'jql' in data.keys():
            if(len(myJql) != 0):
                myJql += " OR "
            myJql += data['jql']

        jql = myJql
        try:
            issues = jira.jql(jql)['issues']
            for issue in issues:
                ticket_response = {}
                key = issue['key']
                obj = pokerboard_models.Ticket.objects.filter(ticket_id=key)
                if obj.exists():
                    ticket_response['message'] = 'Ticket part of another pokerboard.'
                    ticket_response['status_code'] = status.HTTP_400_BAD_REQUEST
                else:
                    ticket_response['estimate'] = issue['fields']['customfield_10016']
                    ticket_response['status_code'] = status.HTTP_200_OK
                ticket_response['key'] = key
                ticket_responses.append(ticket_response)
        except requests.exceptions.RequestException as e:
            raise serializers.ValidationError("Invalid Query")
        return ticket_responses

    def create(self, validated_data):
        count = 0
        new_pokerboard = {key: val for key, val in self.data.items() if key not in [
            'sprint_id', 'tickets']}
        ticket_responses = new_pokerboard.pop('ticket_responses')
        if len(ticket_responses) == 0:
            raise serializers.ValidationError("Invalid Sprint!")
        pokerboard = pokerboard_models.Pokerboard.objects.create(**new_pokerboard)
        for ticket_response in ticket_responses:
            if ticket_response['status_code'] != 200:
                continue
            new_ticket_data = {}
            new_ticket_data['pokerboard'] = pokerboard
            new_ticket_data['ticket_id'] = ticket_response['key']
            count += 1
            new_ticket_data['order'] = count
            ticket_id = ticket_response['key']
            ticket_response.pop('key')
            pokerboard_models.Ticket.objects.get_or_create(
                ticket_id=ticket_id, defaults={**new_ticket_data})
            ticket_response['key'] = ticket_id
        return pokerboard


class InviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = pokerboard_models.Invite
        fields = '__all__'
        extra_kwargs = {
            'is_accepted': {'read_only': True}
        }


class InviteCreateSerializer(serializers.Serializer):
    group_id = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), required=False)
    email = serializers.EmailField(required=False)
    user_role = serializers.ChoiceField(
        choices=constants.ROLE_CHOICES, required=False)

    def validate(self, attrs):
        pokerboard_id = self.context['pokerboard']
        method = self.context['method']
        users = []

        if method in ['DELETE', 'POST']:
            if 'group_id' in attrs.keys():
                group = attrs['group_id']
                users = group.users.all()
            
            elif 'email' in attrs.keys():
                try:
                    user = User.objects.get(email=attrs['email'])
                    users.append(user)
                except User.DoesNotExist as e:
                    # TODO Send mail to user
                    raise serializers.ValidationError(e)
            else:
                raise serializers.ValidationError('Provide group_id/email!')

            pokerboard = pokerboard_models.Pokerboard.objects.get(id=pokerboard_id)
            for user in users:

                if pokerboard.manager == user:
                    raise serializers.ValidationError(
                        'Manager cannot be invited!')

                invite = pokerboard_models.Invite.objects.filter(
                    user=user.id, pokerboard=pokerboard_id)

                if method == 'POST' and invite.exists():
                    if invite[0].is_accepted:
                        raise serializers.ValidationError(
                            'Already part of pokerboard')
                    else:
                        raise serializers.ValidationError(
                            'Invite already sent!')

                elif method == 'DELETE':
                    if not invite.exists():
                        raise serializers.ValidationError('User not invited!')
                    elif invite.exists() and invite[0].is_accepted:
                        raise serializers.ValidationError(
                            'Accepted invites cannot be revoked.')

        elif method in ['PATCH']:
            user = self.context['user']
            invite = pokerboard_models.Invite.objects.filter(
                user=user, pokerboard=pokerboard_id)
            if not invite.exists():
                raise serializers.ValidationError('Invite doesnt exists')
            if invite.exists() and invite[0].is_accepted:
                raise serializers.ValidationError('Invite already accepted!')

        return super().validate(attrs)


class PokerBoardUserGroupSerialzier(serializers.ModelSerializer):
    """
    Serializer to fetch group name and id for users belonging to
    a particular pokerboard
    """
    class Meta:
        model = Group
        fields = ['id', 'name']


class PokerboardUserSerializer(serializers.ModelSerializer):
    """
    Serialier to list members belonging to a pokerboard
    """
    user = UserSerializer()
    role = serializers.SerializerMethodField()
    group = PokerBoardUserGroupSerialzier()

    class Meta:
        model = pokerboard_models.PokerboardUser
        fields = ['id', 'user', 'role', 'pokerboard', 'group']
    
    def get_role(self, obj):
        return obj.get_role_display()
