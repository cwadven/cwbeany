from django.conf import settings
from django.core.mail import (
    EmailMessage,
    send_mail,
)
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_email(title: str, html_body_content: str, payload: dict, to: list) -> None:
    """
    title: 메일 제목
    html_body_content: 적용할 templates 폴더에 있는 html 파일 위치
    payload: 해당 template_tag 로 쓰일 값들
    to: 보낼 사람들 (리스트로 전달 필요)
    """
    message = render_to_string(
        html_body_content,
        payload
    )
    send_mail(
        title,
        strip_tags(message),
        settings.EMAIL_HOST_USER,
        to,
        html_message=message,
        fail_silently=False,
    )


def send_email_with_file(title: str, html_body_content: str, payload: dict, to: str, file_path: str) -> None:
    """
    title: 메일 제목
    html_body_content: 적용할 templates 폴더에 있는 html 파일 위치
    payload: 해당 template_tag 로 쓰일 값들
    to: 보낼 사람들 (리스트로 전달 필요)
    file_path: 첨부할 파일 경로
    """
    message = render_to_string(
        html_body_content,
        payload
    )
    email = EmailMessage(
        title,
        strip_tags(message),
        settings.EMAIL_HOST_USER,
        [to],
    )
    if file_path:
        email.attach_file(file_path)
    email.send()
