import signal

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models.deletion import ProtectedError
from guide.models import Program
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
        try:
            api_url = f"{settings.MIRAKURUN_API}/programs"
            response = requests.get(api_url)
            response.raise_for_status()  # HTTPエラーをチェック
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to retrieve data from API: {e}")
            )
            return
        api_data = response.json()

        # APIから取得したデータを処理
        if not response.status_code == 200:
            self.stdout.write(self.style.ERROR("Failed to retrieve data from API"))

        # 番組データの新規作成・更新
        for item in api_data:
            program, created = create_or_update_program(item)
            if program:
                if created:
                    # self.stdout.write(self.style.SUCCESS(f'Successfully created program {program.title}'))
                    pass
                else:
                    # self.stdout.write(self.style.SUCCESS(f'Successfully updated program {program.title}'))
                    program.is_removed = False
                    program.save()
            else:
                # self.stdout.write(self.style.WARNING('Program was ignored due to related items mismatch'))
                pass
            if self.shutdown_flag:
                self.stdout.write(self.style.ERROR("Abort program syncing"))
                break

        api_program_ids = {item["id"] for item in api_data}

        db_programs = Program.objects.all()
        db_program_ids = {program.program_id for program in db_programs}

        programs_to_delete = db_program_ids - api_program_ids

        for program_id in programs_to_delete:
            try:
                program = Program.objects.get(program_id=program_id)
                if program.is_removed:
                    continue
                try:
                    program.delete()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully deleted program with ID {program_id}"
                        )
                    )
                except ProtectedError:
                    program.is_removed = True
                    program.save()
                    self.stdout.write(
                        self.style.WARNING(
                            f"Cannot delete program with ID {program_id} because it is referenced by a protected foreign key"
                        )
                    )
            except Program.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Program with ID {program_id} does not exist")
                )
            if self.shutdown_flag:
                self.stdout.write(self.style.ERROR("Abort program syncing"))
                break

        self.stdout.write(self.style.SUCCESS("Sync programs complete"))
