import json
from datetime import datetime
from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.pokerboard import (
    models as poker_models,
    serializer as poker_serializers
)
from apps.user import (
    serializers as user_serializers
)
from atlassian import Jira

class TestConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """
        To connect user to socket
        check if user is authenticated
        """
        if type(self.scope["user"]) == AnonymousUser:
            await self.close()
        else:
            diction = dict((query.split('=') for query in self.scope['query_string'].decode().split("&")))
            self.user = self.scope['user']
            self.ticket_id = self.scope['url_route']['kwargs']['id']
            self.pokerboard_id = diction.get('pid', None)
            self.manager_id = poker_models.Ticket.objects.get(id=self.ticket_id).pokerboard.manager.id

            if not poker_models.PokerboardUser.objects.filter(
                    user=self.user.id, pokerboard=self.pokerboard_id).exists() and self.user.id!=self.manager_id:
                await self.close()
            else:
                self.session_group_name = 'session_%s' % self.ticket_id

                await self.channel_layer.group_add(
                    self.session_group_name,
                    self.channel_name,
                )
                clients = getattr(self.channel_layer, self.session_group_name, [])
                clients.append(self.scope["user"])
                setattr(self.channel_layer, self.session_group_name, clients)
                await self.accept()


    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            serializer = poker_serializers.ValidateMessageSerializer(data=text_data_json)
            serializer.is_valid(raise_exception=True)
            message = text_data_json['message']
            message_type = text_data_json['message_type']
            method_to_call = getattr(self, message_type)
            res = await method_to_call({
                'type': message_type,
                'message': message,
                'user': self.scope["user"].id
            })
            # Send message to room group
            if res:
                await self.channel_layer.group_send(
                    self.session_group_name,
                    {
                        'type': 'broadcast',
                        'message': res
                    }
                )
        except serializers.ValidationError:
            await self.send(text_data=json.dumps({
                "error": "Something went wrong"
            }))

    async def initialise_game(self, event):
        """
        Initialise game, fetches connceted users and votes already given
        """
        votes = poker_models.UserTicketEstimate.objects.filter(ticket_id=self.ticket_id)
        vote_serializer = poker_serializers.VoteSerializer(instance=votes, many=True)
        clients = list(set(getattr(self.channel_layer, self.session_group_name, [])))
        serializer = user_serializers.UserSerializer(instance=clients, many=True)
        self.session = poker_models.Ticket.objects.filter(id=self.ticket_id).first()
        return {
            "type": event["type"],
            "votes": vote_serializer.data,
            "users": serializer.data,
            "timer": json.dumps(self.session.start_datetime, default=self.iso_format)
        }

    async def start_timer(self, event):
        """
        Starts timer on current voting session
        """
        manager = self.session.pokerboard.manager
        if self.scope["user"] == manager and self.session.status == poker_models.Ticket.ONGOING:
            now = datetime.now()
            self.session.start_datetime = now
            self.session.save()
            return {
                "type": event["type"],
                "start_datetime": json.dumps(now, default=self.iso_format),
            }
        else:
            await self.send(text_data=json.dumps({
                "error": "Can't start timer"
            }))

    def iso_format(self, o):
        if isinstance(o, datetime):
            return o.__str__()

    async def estimate(self, event):
        """
        Finalize estimation of a ticket.
        """
        try:
            manager = self.session.pokerboard.manager
            if self.scope["user"] == manager:
                self.session.status = poker_models.Ticket.ESTIMATED
                self.session.estimate = event["message"]["estimate"]

                jira_manager = poker_models.ManagerCredentials.objects.get(user=manager)
                jira = Jira(
                    url = jira_manager.url,
                    username = jira_manager.username,
                    password = jira_manager.password,
                )

                fields = {'customfield_10016': event["message"]["estimate"]}
                jira.update_issue_field(self.session.ticket_id, fields)

                self.session.save()

                return {
                    "type": event["type"],
                    "estimate": event["message"]["estimate"]
                }
            else:
                await self.send(text_data=json.dumps({
                    "error": "Only manager can finalize estimate"
                }))
        except serializers.ValidationError as e:
            await self.send(text_data=json.dumps({
                "error": "Estimation failed"
            }))

    async def disconnect(self, close_code):
        """
        Disconnect users from socket
        """
        if hasattr(self, 'session_group_name'):
            await self.channel_layer.group_discard(
                self.session_group_name,
                self.channel_name
            )

            await self.channel_layer.group_send(
                self.session_group_name,
                {
                    "type": "broadcast",
                    "message": f'User {self.user} has left the group.',
                    "user": user_serializers.UserSerializer(self.user).data,  #is there any need for this?
                }
            )

            print("disconnected")

    async def broadcast(self, event):
        """
        Broadcast a message to connected channels in current group
        """
        await self.send(text_data=json.dumps(event["message"]))
