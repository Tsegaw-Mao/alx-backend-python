#!/usr/bin/env python3
"""Views for the chats app."""

from rest_framework import viewsets, filters as drf_filters
from django_filters import rest_framework as filters
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer

from .permissions import IsParticipantOfConversation
from rest_framework.permissions import IsAuthenticated


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and creating Conversations."""

    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (drf_filters.SearchFilter, filters.DjangoFilterBackend)
    search_fields = ['participants__email', 'participants__first_name']
    filterset_fields = ['participants__user_id']
    
    def get_queryset(self):
        # Only show conversations where the user is a participant
        return Conversation.objects.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Create a new conversation with given participant user IDs.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """ViewSet for listing and sending messages in conversations."""

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [ IsAuthenticated, IsParticipantOfConversation ]
    filter_backends = (drf_filters.SearchFilter, filters.DjangoFilterBackend)
    search_fields = ['message_body', 'sender__email']
    filterset_fields = ['conversation__conversation_id', 'sender__user_id']
    
    def get_queryset(self):
        # Filter messages to only those where the user is a participant
        return Message.objects.filter(Conversation_participants=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Send a new message to an existing conversation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
