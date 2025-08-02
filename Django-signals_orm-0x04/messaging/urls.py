#!/usr/bin/env python3
"""Chats app URL configuration using nested routers."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, delete_user

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested router for messages under conversations
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path("account/delete/", delete_user, name="delete_user"),
]

def build_thread(message):
    """Recursively builds a threaded conversation."""
    thread = {
        'message': message,
        'replies': [build_thread(reply) for reply in message.replies.all()]
    }
    return thread
