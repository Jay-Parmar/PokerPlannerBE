from rest_framework import serializers, status

from apps.pokerboard.models import Pokerboard, Ticket
from apps.user.models import User
from apps.user.serializers import UserSerializer

from django.conf import settings

import requests


class TicketsSerializer(serializers.ListSerializer):
    child = serializers.CharField()


class PokerBoardCreationSerializer(serializers.ModelSerializer):
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())
    sprint_id = serializers.CharField(required=False)
    tickets = TicketsSerializer(required=False)
    ticket_responses = serializers.SerializerMethodField()

    class Meta:
        model = Pokerboard
        fields = [
            'manager_id', 'title', 'description', 'tickets', 'sprint_id', 'ticket_responses'
        ]

    def get_ticket_responses(self, instance):
        jira = settings.JIRA
        data = dict(instance)
        ticket_responses = []
        i = 0
        # If sprint, then fetch all tickets in sprint and add
        if 'sprint_id' in data:
            sprint_id = data['sprint_id']
            while True:
                issues = []
                try:
                    issues = jira.get_sprint_issues(
                        sprint_id, i*50, 50)['issues']
                    data['tickets'] = []
                    for issue in issues:
                        data['tickets'].append(issue['key'])
                except requests.exceptions.RequestException as e:
                    return []
                i += 1
                if len(issues) < 50:
                    break

        # Adding tickets
        if 'tickets' in data.keys():
            tickets = data['tickets']
            serializer = TicketsSerializer(data=tickets)
            serializer.is_valid(raise_exception=True)

            for ticket in tickets:
                ticket_response = {}
                try:
                    # Check if ticket is already part of another pokerboard
                    obj = Ticket.objects.filter(ticket_id=ticket)
                    if obj.exists():
                        raise Exception('Ticket part of another pokerboard.')
                    # Checking with JIRA
                    jira_response = jira.issue(key=ticket)['fields']
                    ticket_response["summary"] = jira_response["summary"]
                    ticket_response['estimate'] = jira_response['customfield_10016']
                    ticket_response['status_code'] = status.HTTP_200_OK
                except Exception as e:
                    ticket_response['message'] = str(e)
                    ticket_response['status_code'] = status.HTTP_404_NOT_FOUND

                ticket_response['key'] = ticket
                ticket_responses.append(ticket_response)
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
