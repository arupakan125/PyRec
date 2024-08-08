import signal

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from guide.utils import create_or_update_program


class Command(BaseCommand):
    help = "Load program data from API"

    def handle(self, *args, **kwargs):
        self.shutdown_flag = False

        def signal_handler(signum, frame):
            self.shutdown_flag = True
            self.stdout.write(self.style.WARNING("Shutting down..."))

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # APIからデータを取得
        api_url = f"{settings.MIRAKURUN_API}/programs"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            for item in data:
                program, created = create_or_update_program(item)
                if program:
                    if created:
                        # self.stdout.write(self.style.SUCCESS(f'Successfully created program {program.title}'))
                        pass
                    else:
                        # self.stdout.write(self.style.SUCCESS(f'Successfully updated program {program.title}'))
                        pass
                else:
                    # self.stdout.write(self.style.WARNING('Program was ignored due to related items mismatch'))
                    pass
                if self.shutdown_flag:
                    break
        else:
            self.stdout.write(self.style.ERROR("Failed to retrieve data from API"))
