import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, User


class User(AbstractUser):
    """
    Custom User model with UUID and required additional fields.
    """
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    email = models.EmailField(unique=True, null=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    class Role(models.TextChoices):
        GUEST = 'guest', 'Guest'
        HOST = 'host', 'Host'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        null=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # Override username field behavior
    username = models.CharField(max_length=150, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    @property
    def password_hash(self):
        """Alias for the Django hashed password field."""
        return self.password

    def __str__(self):
        return f"{self.email} ({self.role})"


class Conversation(models.Model):
    """
    Conversation with multiple participants.
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    """
    Represents a message sent in a conversation.
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='messages_sent'
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    message_body = models.TextField(
        null=False
    )
    sent_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Message from {self.sender.email} at {self.sent_at}"
    
