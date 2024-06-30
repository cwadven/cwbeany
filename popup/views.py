from django.http import HttpResponse

from common.common_utils.string_utils import get_filtered_by_startswith_text_and_convert_to_standards
from popup.dtos.object_dtos import PopupModalItem
from popup.dtos.response_dtos import PopupModalResponse
from popup.mappers import POPUP_MODAL_MAPPER
from popup.services import get_active_popups


def get_popup_modal(request, modal_type_name: str):
    excluded_modal_ids = get_filtered_by_startswith_text_and_convert_to_standards(
        modal_type_name,
        request.COOKIES.keys(),
        is_integer=True,
    )
    modal = POPUP_MODAL_MAPPER.get(modal_type_name)
    if not modal:
        return HttpResponse(
            PopupModalResponse(
                modals=[],
                keyword=modal_type_name,
            ).model_dump_json(),
            'application/json',
        )

    active_popups = get_active_popups(modal)
    return HttpResponse(
        PopupModalResponse(
            modals=[
                PopupModalItem.of(popup, top=index * 50, left=index * 50)
                for index, popup in enumerate(
                    active_popups.exclude(id__in=excluded_modal_ids).order_by('-sequence', 'id'),
                    start=1
                )
            ],
            keyword=modal_type_name,
        ).model_dump_json(),
        'application/json',
    )
