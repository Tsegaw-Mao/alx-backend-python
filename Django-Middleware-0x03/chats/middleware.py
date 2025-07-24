# messaging_app/middleware.py

import logging
from datetime import datetime
from django.http import HttpResponseForbidden

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("request_logger")
        handler = logging.FileHandler("requests.log")  # log file
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):
         # Define allowed access window
        now = datetime.now().time()
        start_time = time(18, 0)  # 6:00 PM
        end_time = time(21, 0)    # 9:00 PM
        
         # Only block API/chat paths; adjust if needed
        if request.path.startswith("/api/"):
            if not (start_time <= now <= end_time):
                return HttpResponseForbidden(
                    "<h1>Access to the messaging app is only allowed between 6PM and 9PM.</h1>"
                )

        response = self.get_response(request)
        
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        return response
