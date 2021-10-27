import requests

from atlassian import Jira
from decouple import config
from django.conf import settings
from rest_framework import serializers, status

from apps.pokerboard import models as pokerboard_models
from apps.user import models as user_models
from apps.user import serializers as user_serializer


class GetTicketsSerializer(serializers.ListSerializer):
    child = serializers.CharField()


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = pokerboard_models.Ticket
        fields = ['pokerboard', 'ticket_id', 'order', 'status']


class PokerBoardSerializer(serializers.ModelSerializer):
    manager = user_serializer.UserSerializer()
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
    manager_id = serializers.PrimaryKeyRelatedField(queryset=user_models.User.objects.all())
    sprint_id = serializers.CharField(required=False, write_only=True)
    tickets = GetTicketsSerializer(required=False, write_only=True)
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
            serializer = GetTicketsSerializer(data=tickets)
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
            if(len(jql)==0):
                raise serializers.ValidationError("Invalid Query")
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
        valid_tickets = 0
        for ticket_response in ticket_responses:
            valid_tickets += ticket_response['status_code'] == 200

        if valid_tickets == 0:
            raise serializers.ValidationError('Invalid tickets!')
        manager = user_models.User.objects.get(id=new_pokerboard["manager"]) 
        new_pokerboard["manager"] = manager
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
                ticket_id=ticket_id, defaults={**new_ticket_data}
            )
            ticket_response['key'] = ticket_id
        return pokerboard


class PokerboardUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = pokerboard_models.PokerboardUser
        fields = ['user', 'role', 'pokerboard']
