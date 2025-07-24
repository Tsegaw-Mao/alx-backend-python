# messaging_app/middleware.py

import logging
from datetime import datetime, time
from django.http import HttpResponseForbidden


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("request_logger")
        handler = logging.FileHandler("requests.log")  # log file
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, request):
        user = request.user if request.user.is_authenticated else "Anonymous"
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"
        self.logger.info(log_message)
        return self.get_response(request)


class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Define allowed access window
        now = datetime.now().time()
        start_time = time(18, 0)  # 6:00 PM
        end_time = time(21, 0)  # 9:00 PM

        # Only block API/chat paths; adjust if needed
        if request.path.startswith("/api/"):
            if not (start_time <= now <= end_time):
                return HttpResponseForbidden(
                    "<h1>Access to the messaging app is only allowed between 6PM and 9PM.</h1>"
                )

        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.message_logs = {}  # Stores request timestamps per IP

    def __call__(self, request):
        ip = self.get_client_ip(request)

        if request.method == "POST" and request.path.startswith("/api/messages"):
            now = datetime.now()
            window = timedelta(minutes=1)

            if ip not in self.message_logs:
                self.message_logs[ip] = []

            # Filter out timestamps outside the 1-minute window
            self.message_logs[ip] = [
                timestamp
                for timestamp in self.message_logs[ip]
                if now - timestamp < window
            ]

            if len(self.message_logs[ip]) >= 5:
                return HttpResponseForbidden(
                    "Message rate limit exceeded. Please wait a minute."
                )

            self.message_logs[ip].append(now)

        return self.get_response(request)

    def get_client_ip(self, request):
        """Get real client IP even behind proxies."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
