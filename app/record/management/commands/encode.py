import signal

from django.conf import settings
from django.core.management.base import BaseCommand
from guide.utils import create_or_update_program
from record.tasks import encode


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        encode()
