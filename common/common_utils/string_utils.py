from typing import (
    List,
    Sequence,
    Union,
)


def get_filtered_by_startswith_text_and_convert_to_standards(startswith_text: str,
                                                             keys: Sequence,
                                                             is_integer=False) -> List[Union[int, str]]:
    """
    반복을 할 수 있는 타입에서 특정 텍스트로 시작하는 키를 필터링하면서
    특정 부분의 키의 값을 정수로 변환할 수 있는지 여부에 따라

    [ 예 ]
    startswith_text 가 'home_popup_modal_' 인 경우
    ['home_popup_modal_1', 'home_popup_modal_2', 'home_popup_modal_3', 'home_popup_modal_4', 'k_popup_modal_10']
    ['1', '2', '3', '4']
    와 같이 바꾸는 것
    """
    return [
        int(key.replace(startswith_text, '')) if is_integer else key.replace(startswith_text, '')
        for key in keys if key.startswith(startswith_text)
    ]
