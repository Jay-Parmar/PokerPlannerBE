import json
from datetime import datetime
from django.contrib.auth.models import AnonymousUser
from django.db.models import Max
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


class SessionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """
        To connect user to socket
        check if user is authenticated
        """
        if type(self.scope["user"]) == AnonymousUser:
            await self.close()
        else:
            diction = dict(
                (query.split('=') for query in self.scope['query_string'].decode().split("&")))
            self.user = self.scope['user']
            self.ticket_id = self.scope['url_route']['kwargs']['id']
            self.pokerboard_id = diction.get('pid', None)
            self.manager_id = poker_models.Ticket.objects.get(
                id=self.ticket_id).pokerboard.manager.id

            if not poker_models.PokerboardUser.objects.filter(
                    user=self.user.id, pokerboard=self.pokerboard_id).exists() and self.user.id != self.manager_id:
                await self.close()
            else:
                print("::inside else")
                self.session_group_name = 'session_%s' % self.ticket_id

                await self.channel_layer.group_add(
                    self.session_group_name,
                    self.channel_name,
                )
                clients = getattr(self.channel_layer,
                                  self.session_group_name, [])
                clients.append(self.scope["user"])
                setattr(self.channel_layer, self.session_group_name, clients)
                await self.accept()

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
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
                'type': 'error',
                'error': "Something went wrong"
            }))

    async def initialise_game(self, event):
        """
        Initialise game, fetches connceted users and votes already given
        """
        votes = poker_models.UserTicketEstimate.objects.filter(
            ticket_id=self.ticket_id)
        vote_serializer = poker_serializers.VoteSerializer(
            instance=votes, many=True)
        clients = list(
            set(getattr(self.channel_layer, self.session_group_name, [])))
        query_set = poker_models.PokerboardUser.objects.filter(user__in=clients, pokerboard=self.pokerboard_id)
        serializer = poker_serializers.PokerBoardVotingUserSerializer(instance=query_set, many=True)
        self.session = poker_models.Ticket.objects.filter(
            id=self.ticket_id).first()
        return {
            "type": event["type"],
            "votes": vote_serializer.data,
            "users": serializer.data,
            "timer": json.dumps(self.session.start_datetime, default=self.myconverter)
        }

    async def start_timer(self, event):
        """
        Starts timer on current voting session
        """
        manager = self.session.pokerboard.manager
        if self.scope["user"] == manager and self.session.status != poker_models.Ticket.ESTIMATED:
            now = datetime.now()
            self.session.start_datetime = now
            self.session.status = poker_models.Ticket.ONGOING
            self.session.save()
            return {
                "type": event["type"],
                "start_datetime": json.dumps(now, default=self.myconverter),
            }
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': "Can't start timer"
            }))

    def myconverter(self, obj):
        """
        convert datetime into json
        """
        if isinstance(obj, datetime):
            return obj.__str__()

    async def vote(self, event):
        """
        Places/update a vote on a ticket
        """
        try:
            context = {"user": self.scope['user'].id,
                       'ticket_id': self.session.id}
            serializer = poker_serializers.VoteSerializer(
                data=event["message"], context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return {
                "type": event["type"],
                "vote": serializer.data
            }
        except serializers.ValidationError as e:
            print(e)
            await self.send(text_data=json.dumps({
                'type': 'error',
                'error': "Invalid estimate"
            }))

    async def estimate(self, event):
        """
        Finalize estimation of a ticket.
        """
        try:
            manager = self.session.pokerboard.manager
            if self.scope["user"] == manager:
                self.session.status = poker_models.Ticket.ESTIMATED
                self.session.estimate = event["message"]["estimate"]
                now = datetime.now()
                self.session.end_datetime = now
                jira_manager = poker_models.ManagerCredentials.objects.get(
                    user=manager)
                jira = Jira(
                    url=jira_manager.url,
                    username=jira_manager.username,
                    password=jira_manager.password,
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
                        'type': 'error',
                        "error": "Only Manager can set final estimate"
                    }))
        except serializers.ValidationError as e:
            await self.send(text_data=json.dumps({
                    'type': 'error',
                    "error": "Error occoured while estimating"
                }))

    async def disconnect(self, code):
        """
        Runs when a user disconnects
        """
        clients = getattr(self.channel_layer, self.session_group_name, [])
        clients.remove(self.scope["user"])
        setattr(self.channel_layer, self.session_group_name, clients)
        serializer = user_serializers.UserSerializer(
            list(set(clients)), many=True)
        await self.channel_layer.group_send(
            self.session_group_name,
            {
                'type': 'broadcast',
                'message': {
                    'type': 'leave',
                    'users': serializer.data
                }
            }
        )
        await self.channel_layer.group_discard(self.session_group_name, self.channel_name)

    async def broadcast(self, event):
        """
        Broadcast a message to connected channels in current group
        """
        await self.send(text_data=json.dumps(event["message"]))

    async def skip(self, event):
        """
        Skip current voting session
        """
        manager = self.manager_id
        print(self.scope["user"].id)
        print(self.session.status)
        if self.scope["user"].id == manager and self.session.status != poker_models.Ticket.ESTIMATED:
            self.session.status = poker_models.Ticket.SKIPPED
            self.session.save()
            self.move_ticket_to_end()
            return {
                "type": event["type"],
            }
        else:
            await self.send(text_data=json.dumps({
                    'type': 'error',
                    "error": "Can't skip"
                }
            ))

    def move_ticket_to_end(self):
        max_order = poker_models.Ticket.objects.filter(pokerboard=self.pokerboard_id).aggregate(Max('order'))
        if max_order:
            val = max_order['order__max']
            val = val + 1
            self.session.order = val
            self.session.save()
