from config.cron import get_chatgpt_lesson
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        get_chatgpt_lesson()
