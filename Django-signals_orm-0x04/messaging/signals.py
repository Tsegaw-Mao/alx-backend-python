from django.contrib.auth.models import User
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver
from .models import Message, MessageHistory, Notification

@receiver(post_delete, sender=Message)
def cleanup_user_related_data(sender, instance, **kwargs):
    # Optional cleanup if not using CASCADE or need extra behavior

    # Delete all messages where user was sender or receiver (if not cascaded)
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()

    # Delete notifications
    Notification.objects.filter(user=instance).delete()

    # Delete message histories edited by this user (if not cascaded)
    MessageHistory.objects.filter(edited_by=instance).delete()

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    if not instance.pk:
        # New message, no history to save
        return

    try:
        old_message = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return

    # If content has changed, save the old content to history
    if old_message.content != instance.content:
        MessageHistory.objects.create(
            message=instance,
            old_content=old_message.content
        )
        # Mark the message as edited
        instance.edited = True
        
@receiver(post_save, sender=Message)
def create_notification_on_new_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )
