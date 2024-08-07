import requests
import json
import signal
from django.conf import settings
from django.core.management.base import BaseCommand
from guide.utils import create_or_update_program
from guide.models import Program

class Command(BaseCommand):
    help = 'Process program events from the event stream'

    def handle(self, *args, **kwargs):
        self.shutdown_flag = False

        def signal_handler(signum, frame):
            self.shutdown_flag = True
            self.stdout.write(self.style.WARNING('Shutting down...'))

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        try:
            api_url = f"{settings.MIRAKURUN_API}/events/stream"
            response = requests.get(api_url, stream=True)
            response.raise_for_status()  # HTTPエラーをチェック
        except requests.exceptions.RequestException as e:
            self.stdout.write(self.style.ERROR(f'Failed to connect to event stream: {e}'))
            return

        for line in response.iter_lines():
            if self.shutdown_flag:
                break
            if line:
                # 先頭の `[` やイベントごとのカンマ `,` を無視
                line = line.lstrip(b'[,').strip()
                if not line:
                    continue

                try:
                    event = json.loads(line.decode('utf-8'))
                except json.JSONDecodeError as e:
                    self.stdout.write(self.style.ERROR(f'Failed to decode JSON: {e}'))
                    continue

                if event.get('resource') == 'program':
                    if event.get('type') in ['create', 'update']:
                        program_data = event.get('data', {})
                        program, created = create_or_update_program(program_data)
                        if program:
                            if created:
                                self.stdout.write(self.style.SUCCESS(f'Successfully created program {program.title}'))
                            else:
                                self.stdout.write(self.style.SUCCESS(f'Successfully updated program {program.title}'))
                        else:
                            self.stdout.write(self.style.WARNING('Program was ignored due to related items mismatch'))
                    elif event.get('type') == 'remove':
                        program_id = event.get('data', {}).get('id')
                        if program_id:
                            try:
                                program = Program.objects.get(program_id=program_id)
                                program.delete()
                                self.stdout.write(self.style.SUCCESS(f'Successfully deleted program with ID {program_id}'))
                            except Program.DoesNotExist:
                                self.stdout.write(self.style.ERROR(f'Program with ID {program_id} does not exist'))
                            except Exception as e:
                                self.stdout.write(self.style.ERROR(f'Failed to delete program with ID {program_id}: {e}'))

        self.stdout.write(self.style.SUCCESS('Program event processing stopped.'))
