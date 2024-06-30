from django.db.models import (
    Q,
    QuerySet,
)
from django.utils import timezone


def get_datetime_active_queryset(datetime_active_qs: QuerySet, now=None) -> QuerySet:
    if now is None:
        now = timezone.now()

    return datetime_active_qs.filter(
        (Q(start_time__lte=now) | Q(start_time__isnull=True)),
        (Q(end_time__gte=now) | Q(end_time__isnull=True)),
        is_active=True,
    )
