import django_filters
from .models import Message


class MessageFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    end_date = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    conversation_id = django_filters.NumberFilter(field_name="conversation__id")

    class Meta:
        model = Message
        fields = ['conversation_id', 'start_date', 'end_date']
