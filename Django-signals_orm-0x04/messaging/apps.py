from django.apps import AppConfig


class ChatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'


class YourAppConfig(AppConfig):
    name = 'your_app_name'

    def ready(self):
        import messaging.signals  # Adjust the import to your app name
