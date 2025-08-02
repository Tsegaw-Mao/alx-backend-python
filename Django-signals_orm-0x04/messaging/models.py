import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, User


class User(AbstractUser):
    """
    Custom User model with UUID and required additional fields.
    """

    user_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    email = models.EmailField(unique=True, null=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    class Role(models.TextChoices):
        GUEST = "guest", "Guest"
        HOST = "host", "Host"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=10, choices=Role.choices, null=False)

    created_at = models.DateTimeField(auto_now_add=True)

    # Override username field behavior
    username = models.CharField(max_length=150, blank=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

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
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)  # New field
    edited_by = models.ForeignKey(  # <-- NEW FIELD
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name="edited_messages"
    )


    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"


class MessageHistory(models.Model):
    message = models.ForeignKey(Message, related_name="history", on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(  # <-- Optional for audit trail
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"History of message {self.message.id} at {self.edited_at}"


class Notification(models.Model):
    user = models.ForeignKey(
        User, related_name="notifications", on_delete=models.CASCADE
    )
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} (Read: {self.is_read})"
