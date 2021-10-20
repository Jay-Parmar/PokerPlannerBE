from rest_framework import serializers, status

from apps.pokerboard.models import Pokerboard, Ticket, ManagerCredentials
from apps.user.models import User
from apps.user.serializers import UserSerializer

from django.conf import settings

from atlassian import Jira
from decouple import config

import requests


class TicketsSerializer(serializers.ListSerializer):
    child = serializers.CharField()


class ManagerLoginSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ManagerCredentials
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
        model = Pokerboard
        fields = [
            'manager_id', 'title', 'description', 'tickets', 'sprint_id',
            'ticket_responses', 'jql'
        ]

    def get_ticket_responses(self, instance):
        user_obj = list(instance.items())[0][-1]
        manager = ManagerCredentials.objects.get(user=user_obj)
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
                obj = Ticket.objects.filter(ticket_id=key)
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
        pokerboard = Pokerboard.objects.create(**new_pokerboard)
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
            Ticket.objects.get_or_create(
                ticket_id=ticket_id, defaults={**new_ticket_data})
            ticket_response['key'] = ticket_id
        return pokerboard
