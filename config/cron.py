import os
import pymysql
import datetime

from django.conf import settings

from chatgpt.dtos.common_dtos import ChatGPTConversationEntry
from chatgpt.models import (
    Lesson,
    LessonInformation,
)
from chatgpt.services import get_chatgpt_response
from common.common_utils.io_utils import send_email, send_email_with_file
from common.consts.common_consts import (
    EMAIL_TEMPLATE_MAPPER,
    HEALTH_CHECK, BACKUP_SQL,
)
from control.models import (
    TodayYesterday,
    IPVisitant,
)


def update_yesterday_and_today_visitor():
    """
    하루에 한번씩 TodayYesterday 데이터 추가
    """
    yesterday_visitor_info = TodayYesterday.objects.all().last()

    if yesterday_visitor_info:
        print("----created----")
        TodayYesterday.objects.create(
            yesterday=yesterday_visitor_info.today,
            today=0,
        )
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesterday_info = {
            "created_at__year": yesterday.year,
            "created_at__month": yesterday.month,
            "created_at__day": yesterday.day,
        }
        yesterday_date = f"{yesterday_info['created_at__year']}" + "-" + f"{yesterday_info['created_at__month']:02}" + "-" + f"{yesterday_info['created_at__day']:02}"

        print(f"[{yesterday_date}] Yesterday check with before TodayYesterday Field: {yesterday_visitor_info.today}")
        print(f"[{yesterday_date}] Yesterday check with IPVisitant Row Count: {IPVisitant.objects.filter(**yesterday_info).count()}")
        print("-----ended-----")
    else:
        TodayYesterday.objects.create(
            yesterday=0,
            today=1,
        )


def database_backup():
    """
    데이터 베이스 백업
    """
    HOST = settings.DATABASES['default']['HOST']
    NAME = settings.DATABASES['default']['NAME']
    USER = settings.DATABASES['default']['USER']
    PASSWORD = settings.DATABASES['default']['PASSWORD']
    print("----backup sql connecting----")
    conn = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=NAME,
        charset='utf8'
    )

    backup_path = '/var/www/backup'
    backup_file_name = f'nully_blog_{datetime.date.today().strftime("%Y-%m-%d")}.sql'
    os.system(
        f'mysqldump -h {HOST} -u {USER} -p{PASSWORD} {NAME} > {backup_path}/{backup_file_name}')
    print("----backup sql created----")
    conn.close()
    print("----backup sql email sending----")
    send_email_with_file(
        f'[Beany 블로그] {datetime.date.today().strftime("%Y-%m-%d")} 데이터베이스 백업',
        EMAIL_TEMPLATE_MAPPER[BACKUP_SQL],
        {},
        'cwadven@kakao.com',
        backup_path + '/' + backup_file_name,
    )
    print("----backup sql email sended----")


def get_chatgpt_lesson():
    """
    ChatGPT API를 통해 정보를 가져옵니다
    """
    try:
        lesson_information = LessonInformation.objects.all()[0]
    except IndexError:
        print("-----failed to find Lesson Information-----")
        return

    lesson_histories = [
        ChatGPTConversationEntry(role='assistant', content=lesson) for lesson in
        Lesson.objects.filter(
            tag=lesson_information.tag,
        ).values_list('body', flat=True)
    ]
    print("----request----")
    result = get_chatgpt_response(
        system_prompt=lesson_information.system_prompt,
        prompt=lesson_information.prompt,
        conversation_history=lesson_histories,
    )
    Lesson.objects.create(
        summary=lesson_information.summary,
        tag=lesson_information.tag,
        body=result,
    )
    print("----created----")
    print("-----ended-----")


def health_check():
    print("----sending----")
    send_email(
        f'[Beany 블로그] django-cron health check',
        EMAIL_TEMPLATE_MAPPER[HEALTH_CHECK],
        {},
        ['cwadven@kakao.com'],
    )
    print("----sended----")
