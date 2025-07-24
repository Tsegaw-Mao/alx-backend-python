from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsParticipantOfConversation(BasePermission):
    """
    Custom permission to only allow conversation participants to access messages.
    """

    def has_permission(self, request, view):
        # Allow only authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Only participants of the conversation can view, update, or delete messages.
        Assumes `obj` is a Message instance that has a `.conversation` field
        which has a `.participants` many-to-many or related field.
        """
        return request.user in obj.conversation.participants.all()
