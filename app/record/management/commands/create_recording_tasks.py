import signal

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from guide.utils import create_or_update_program


class Command(BaseCommand):
    help = 'Load program data from API'

    def handle(self, *args, **kwargs):
        self.shutdown_flag = False

        def signal_handler(signum, frame):
            self.shutdown_flag = True
            self.stdout.write(self.style.WARNING('Shutting down...'))

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    # To be filled
