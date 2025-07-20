from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer
from rest_framework.exceptions import ValidationError


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and creating Conversations.
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with a list of participant user IDs.
        """
        participants_ids = request.data.get('participants_ids')
        if not participants_ids or not isinstance(participants_ids, list):
            raise ValidationError(
                {"participants_ids": "This field is required and must be a list of user IDs."}
            )
        participants = User.objects.filter(user_id__in=participants_ids)
        if participants.count() != len(participants_ids):
            raise ValidationError({"participants_ids": "One or more users not found."})

        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        conversation.save()
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and sending Messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        """
        Send a message to an existing conversation.
        """
        sender_id = request.data.get('sender_id')
        conversation_id = request.data.get('conversation_id')
        message_body = request.data.get('message_body')

        if not sender_id or not conversation_id or not message_body:
            raise ValidationError(
                {
                    "detail": (
                        "sender_id, conversation_id, and message_body "
                        "are required fields."
                    )
                }
            )

        # Validate sender
        try:
            sender = User.objects.get(user_id=sender_id)
        except User.DoesNotExist:
            raise ValidationError({"sender_id": "Sender user does not exist."})

        # Validate conversation
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            raise ValidationError({"conversation_id": "Conversation does not exist."})

        message = Message.objects.create(
            sender=sender,
            conversation=conversation,
            message_body=message_body
        )
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
