from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsParticipantOfConversation(BasePermission):
    """
    - All participants in a conversation can read (GET) and create (POST) messages.
    - Only the sender of a message can update or delete it.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Must be authenticated
        if not user or not user.is_authenticated:
            return False

        # Allow read and create for participants
        if request.method in SAFE_METHODS or request.method == "POST":
            return user in obj.conversation.participants.all()

        # Only allow update/delete by the original sender
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return user == obj.sender

        return False