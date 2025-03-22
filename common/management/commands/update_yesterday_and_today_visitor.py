from config.cron import update_yesterday_and_today_visitor
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        update_yesterday_and_today_visitor()
