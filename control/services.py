from django.db.models import QuerySet

from control.models import Announce


def get_announces() -> QuerySet[Announce]:
    return Announce.objects.all()
