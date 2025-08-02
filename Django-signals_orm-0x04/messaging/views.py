from django.http import HttpResponseForbidden
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_403_FORBIDDEN

from messaging_app.chats import models
from .models import Message, Conversation
from .serializers import MessageSerializer, ConversationSerializer
from .permissions import IsParticipantOfConversation

from django_filters.rest_framework import DjangoFilterBackend
from .filters import MessageFilter
from .pagination import MessagePagination

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.db.models import Prefetch
from django.contrib import messages
#from .utils import build_thread

@login_required
def delete_user(request):
    user = request.user
    if request.method == "POST":
        user.delete()
        messages.success(request, "Your account and all related data have been deleted.")
        return redirect("home")  # or a goodbye page
    return render(request, "account/delete_confirm.html")

def get_threaded_messages(user):
    # Get all top-level messages sent to or from the user
    messages = Message.objects.filter(
        parent_message__isnull=True
    ).filter(
        models.Q(sender=user) | models.Q(receiver=user)
    ).select_related('sender', 'receiver').prefetch_related(
        Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver'))
    ).order_by('-timestamp')

    return messages

@login_required
def message_thread_view(request, message_id):
    from .models import Message
    root_message = Message.objects.select_related('sender', 'receiver').get(id=message_id)

    if root_message.receiver != request.user and root_message.sender != request.user:
        return HttpResponseForbidden("You are not part of this conversation")

    replies = get_threaded_messages(root_message)
    sender = Message.objects.filter(id=message_id).select_related('sender').first().sender
    return render(request, 'messaging/thread.html', {
        'root_message': root_message,
        'replies': replies,
        'sender': sender
    })


@login_required
def inbox_view(request):
    # Fetch root messages (messages that are not replies)
    messages = Message.objects.filter(receiver=request.user, parent_message__isnull=True)\
        .select_related('sender', 'receiver')\
        .prefetch_related('replies')

    return render(request, 'messaging/inbox.html', {'messages': messages})


@login_required
def unread_messages_view(request):
    unread_messages = Message.unread.for_user(request.user)
    return render(request, 'messaging/unread.html', {
        'unread_messages': unread_messages
    })

def inbox_view(request):
    unread_messages = Message.unread.unread_for_user(request.user).only(
        'id', 'sender', 'timestamp', 'content'
    )
    return render(request, 'messaging/inbox.html', {'messages': unread_messages})

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter  # 🔎 Enable filtering
    pagination_class = MessagePagination

    def get_queryset(self):
        return Message.objects.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        conversation = serializer.validated_data.get("conversation", None)

        if not conversation:
            raise PermissionDenied("conversation_id is required.")

        if self.request.user not in conversation.participants.all():
            return Response(
                {"detail": "You are not a participant of this conversation."},
                status=HTTP_403_FORBIDDEN
            )

        serializer.save(sender=self.request.user)

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        if message.sender != request.user:
            return Response(
                {"detail": "You cannot edit this message."},
                status=HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        if message.sender != request.user:
            return Response(
                {"detail": "You cannot delete this message."},
                status=HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
