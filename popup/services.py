from typing import Type

from common.common_utils.query_utils import get_datetime_active_queryset
from popup.models import Popup


def get_active_popups(popup_class: Type[Popup], now=None):
    return get_datetime_active_queryset(
        popup_class.objects.all(),
        now=now
    )
