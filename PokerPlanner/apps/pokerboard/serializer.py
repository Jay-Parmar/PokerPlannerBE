import requests

from rest_framework import serializers, status

from apps.group import models as group_models
from apps.pokerboard import models as pokerboard_models
from apps.user import (
    models as user_models,
    serializers as user_serializers
)

from atlassian import Jira


class GetTicketsSerializer(serializers.ListSerializer):
    child = serializers.CharField()


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = pokerboard_models.Ticket
        fields = ['id', 'pokerboard', 'ticket_id', 'order', 'status']


class PokerBoardSerializer(serializers.ModelSerializer):
    manager = user_serializers.UserSerializer()
    ticket = TicketSerializer(source='tickets', many=True)

    class Meta:
        model = pokerboard_models.Pokerboard
        fields = ['id', 'manager', 'title', 'description',
                  'estimate_type', 'ticket', 'timer']


class ManagerCredentialSerializer(serializers.ModelSerializer):
    """
    Serializer to get Manager Credentials in Database.
    """
    class Meta:
        model = pokerboard_models.ManagerCredentials
        fields = '__all__'


class ManagerLoginSerializer(serializers.ModelSerializer):
    """
    Serializer to save Manager Credentials in Database.
    """

    class Meta:
        model = pokerboard_models.ManagerCredentials
        fields = ['url', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        """
        Check if jira credentials are correct.
        """
        try:
            jira = Jira(
                url=attrs.get('url'),
                username=attrs.get('username'),
                password=attrs.get('password'),
            )
            response = jira.jql("")
            if not response['total']:
                raise serializers.ValidationError("No issue tickets Found")
        except Exception as err:
            raise serializers.ValidationError("Invalid Credentials")

        return attrs


class ManagerDetailSerializer(serializers.ModelSerializer):
    """
    Serializer to save Manager Credentials in Database.
    """

    class Meta:
        model = pokerboard_models.ManagerCredentials
        fields = ['url', 'username', 'password']
        extra_kwargs = {
            'password': {'read_only': True},
            'url': {'read_only': True},
            'username': {'read_only': True},
        }


class PokerBoardCreationSerializer(serializers.ModelSerializer):
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=user_models.User.objects.all(), required=False)
    sprint_id = serializers.CharField(required=False, write_only=True)
    tickets = GetTicketsSerializer(required=False, write_only=True)
    jql = serializers.CharField(required=False, write_only=True)
    ticket_responses = serializers.SerializerMethodField()

    class Meta:
        model = pokerboard_models.Pokerboard
        fields = [
            'manager_id', 'title', 'description', 'tickets', 'sprint_id',
            'ticket_responses', 'jql', 'timer'
        ]

    def get_ticket_responses(self, instance):
        user_obj = list(instance.items())[0][-1]
        manager = pokerboard_models.ManagerCredentials.objects.get(
            user=self.context['manager_id'])
        jira = Jira(
            url=manager.url,
            username=manager.username,
            password=manager.password,
        )
        data = dict(instance)
        ticket_responses = []
        i = 0
        myJql = ""

        if 'sprint_id' in data:
            myJql = "Sprint = " + data['sprint_id']

        if 'tickets' in data.keys():
            tickets = data['tickets']
            serializer = GetTicketsSerializer(data=tickets)
            serializer.is_valid(raise_exception=True)

            if(len(myJql) != 0):
                myJql += " OR "
            myJql += "issueKey in ("
            for ticket in tickets:
                myJql = myJql + ticket + ','
            myJql = myJql[:-1] + ')'

        if 'jql' in data.keys():
            if(len(myJql) != 0):
                myJql += " OR "
            myJql += data['jql']

        jql = myJql
        if(len(jql) == 0):
            raise serializers.ValidationError("Invalid Query")
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
        except Exception as e:
            if str(e).startswith("400 Client Error"):
                raise serializers.ValidationError("Invalid Query")
            raise serializers.ValidationError(str(e))
        return ticket_responses

    def create(self, validated_data):
        count = 0
        new_pokerboard = {key: val for key, val in self.data.items() if key not in [
            'sprint_id', 'tickets']}
        ticket_responses = new_pokerboard.pop('ticket_responses')
        valid_tickets = 0
        for ticket_response in ticket_responses:
            valid_tickets += ticket_response['status_code'] == 200

        if valid_tickets == 0:
            raise serializers.ValidationError('Invalid tickets!')
        manager = user_models.User.objects.get(id=self.context['manager_id'])
        new_pokerboard["manager"] = manager
        pokerboard = pokerboard_models.Pokerboard.objects.create(
            **new_pokerboard)
        for ticket_response in ticket_responses:
            if ticket_response['status_code'] != 200:
                continue
            ticket_data = {}
            ticket_data['pokerboard'] = pokerboard
            ticket_data['ticket_id'] = ticket_response['key']
            count += 1
            ticket_data['order'] = count
            ticket_id = ticket_response['key']
            ticket_response.pop('key')
            pokerboard_models.Ticket.objects.get_or_create(
                ticket_id=ticket_id, defaults={**ticket_data}
            )
            ticket_response['key'] = ticket_id
        return pokerboard


class PokerBoardUserGroupSerialzier(serializers.ModelSerializer):
    """
    Serializer to fetch group name and id for users belonging to
    a particular pokerboard
    """
    class Meta:
        model = group_models.Group
        fields = ['id', 'name']


class PokerboardUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = pokerboard_models.PokerboardUser
        fields = ['id', 'user', 'role', 'pokerboard']


class PokerboardTicketSerializer(serializers.ModelSerializer):
    """
    PokerBoard tickets Serializer for updating and listing pokerboard tickets.
    """
    pokerboard = PokerBoardSerializer()

    class Meta:
        model = pokerboard_models.Ticket
        fields = ['id', 'pokerboard', 'ticket_id',
                'estimate', 'order', 'status']
        # TODO: add a methodfield here so that while fetching an  entity from ticket table
        # ticket details come in that request too. and on updatinf final estimate it should be
        # updated on JIRA as well


class CommentSerializer(serializers.Serializer):
    """
    Comment Serializer to comment on a ticket 
    """
    comment = serializers.CharField()
    ticket_id = serializers.SlugField()


class VoteSerializer(serializers.ModelSerializer):
    """
    Vote Serializer for creating and listing votes.
    """
    user = user_serializers.UserSerializer(read_only=True)
    class Meta:
        model = pokerboard_models.UserTicketEstimate
        fields = ["id", "estimate", "ticket_id", "user"]
        extra_kwargs = {
            "ticket_id": {
                "read_only": True
            }
        }

    def validate(self, data):
        print("::: ticket :::", self.context['ticket_id'])
        data['ticket_id'] = self.context['ticket_id']
        data['user'] = self.context['user']
        return super().validate(data)

    def create(self, validated_data):
        """
        Create or update a vote
        """
        vote, created = pokerboard_models.UserTicketEstimate.objects.update_or_create(
            ticket_id_id=validated_data['ticket_id'],
            user_id=validated_data['user'],
            defaults={
                'estimate': validated_data['estimate']
            }
        )
        print(":::Created :::", created)
        return vote


class PokerboardMemberSerializer(serializers.ModelSerializer):
    """
    Serialier to list members belonging to a pokerboard
    """
    user = user_serializers.UserSerializer()
    role = serializers.SerializerMethodField()
    group = PokerBoardUserGroupSerialzier()

    class Meta:
        model = pokerboard_models.PokerboardUser
        fields = ['id', 'user', 'role', 'pokerboard', 'group']

    def get_role(self, obj):
        return obj.get_role_display()
