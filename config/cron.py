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
from common.common_utils.google_utils.google_drive_utils import GoogleDriveServiceGenerator, GoogleDriveService
from common.common_utils.io_utils import (
    send_email,
    send_email_with_file,
)
from common.consts.common_consts import (
    BACKUP_MEDIA,
    BACKUP_SQL,
    EMAIL_TEMPLATE_MAPPER,
    HEALTH_CHECK,
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
        settings.NOTICE_EMAILS,
        backup_path + '/' + backup_file_name,
    )
    print("----backup sql email sended----")


def media_backup():
    """
    미디어 백업
    """
    backup_path = '/var/www/backup'
    backup_file_name = f'cwbeany_blog_media_{datetime.date.today().strftime("%Y-%m-%d")}.tar.gz'
    print("----backup media started----")
    os.system(
        f'tar -zcvf /{backup_path}/{backup_file_name} /var/www/beany_blog/media/'
    )
    print("----backup media file created----")
    print("----backup media file uploading to google drive----")
    google_drive_service = GoogleDriveService(
        service=GoogleDriveServiceGenerator(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE,
            settings.GOOGLE_API_SCOPES,
        ).generate_service()
    )
    file_id = google_drive_service.upload_file_by_file_path(
        file_name=backup_file_name,
        upload_target_file_path=f'/{backup_path}/{backup_file_name}',
        upload_drive_folder_target=settings.GOOGLE_DRIVE_MEDIA_BACKUP_FOLDER_ID,
    )
    redirect_url = f'https://drive.google.com/file/d/{file_id}/view'
    print("----backup media file uploaded to google drive----")
    print("----email notice uploaded to google drive----")
    send_email(
        f'[Beany 블로그] {datetime.date.today().strftime("%Y-%m-%d")} 미디어 백업 완료',
        EMAIL_TEMPLATE_MAPPER[BACKUP_MEDIA],
        {
            'redirect_url': redirect_url,
        },
        settings.NOTICE_EMAILS,
    )
    print("----email sent notice uploaded to google drive----")
    print("----backup media deleting----")
    os.system(f'rm -rf /{backup_path}/{backup_file_name}')
    print("----backup media deleted----")


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
        settings.NOTICE_EMAILS,
    )
    print("----sended----")
