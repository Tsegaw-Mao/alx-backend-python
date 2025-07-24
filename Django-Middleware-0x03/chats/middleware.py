# chats/middleware.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Safely get the user if available
        user = getattr(request, 'user', None)

        logger.info(
            f"{datetime.now()} - User: {user if user and user.is_authenticated else 'Anonymous'} - Path: {request.path}"
        )

        response = self.get_response(request)
        return response
