import requests
from typing import List

from django.db.models import QuerySet

from chatgpt.consts import (
    CHATGPT_HEADERS,
    CHATGPT_URL,
)
from chatgpt.dtos.common_dtos import ChatGPTConversationEntry
from chatgpt.models import (
    Lesson,
    PostSummary,
)


def get_chatgpt_response(
        system_prompt: str,
        prompt: str,
        conversation_history: List[ChatGPTConversationEntry] = None
) -> str:
    if conversation_history is None:
        conversation_history = []

    messages = [
        {'role': 'system', 'content': system_prompt},
    ]
    for entry in conversation_history:
        messages.append({'role': entry.role, 'content': entry.content})
    messages.append({'role': 'user', 'content': prompt})

    response = requests.post(
        url=CHATGPT_URL,
        headers=CHATGPT_HEADERS,
        json={
            'model': 'gpt-4o-mini',
            'messages': messages,
        }
    )
    if response.status_code == 200:
        response_json = response.json()
        generated_text = response_json['choices'][0]['message']['content']
        return generated_text.strip()
    else:
        raise Exception(response.json())


def get_lessons() -> QuerySet[Lesson]:
    return Lesson.objects.all()


def get_latest_post_summary_by_post_id(post_id: int) -> PostSummary:
    return PostSummary.objects.filter(post_id=post_id).order_by('-created_at').first()
