from common.consts.enums import StrValueLabel
from django.conf import settings


CHATGPT_URL = 'https://api.openai.com/v1/chat/completions'
CHATGPT_HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {settings.CHATGPT_KEY}'
}


class LessonSummary(StrValueLabel):
    PYTHON_TIP = ('Python Tip', '파이썬 꿀팁')


class ProcessStatus(StrValueLabel):
    PROCESSING = ('PROCESSING', '처리중')
    DONE = ('DONE', '처리완료')
    FAIL = ('FAIL', '실패')


POST_SUMMARY_SYSTEM_PROMPT = ('너는 테크 블로그에 작성한 내용을 간단하게 요약해주는 비서야.'
                              '요약은 최대 5줄로 해줘. 블로그 글을 분석해서 한글로 요약해줘.'
                              '서두를 붙이지 말고 내용을 바로 요약해줘'
                              '만약 이해를 하지 못했으면 "요약 실패"라고 답해줘.')
