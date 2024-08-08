import requests
from django.core.management.base import BaseCommand
from django.db.models.deletion import ProtectedError
from guide.models import Program


class Command(BaseCommand):
    help = (
        "Sync program data from API and delete programs that are only in the database"
    )

    def handle(self, *args, **kwargs):
        try:
            response = requests.get("http://192.168.1.11:40772/api/programs")
            response.raise_for_status()  # HTTPエラーをチェック
        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f"Failed to retrieve data from API: {e}")
            )
            return

        api_data = response.json()
        api_program_ids = {item["id"] for item in api_data}

        db_programs = Program.objects.all()
        db_program_ids = {program.program_id for program in db_programs}

        programs_to_delete = db_program_ids - api_program_ids

        for program_id in programs_to_delete:
            try:
                program = Program.objects.get(program_id=program_id)
                try:
                    program.delete()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully deleted program with ID {program_id}"
                        )
                    )
                except ProtectedError:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Cannot delete program with ID {program_id} because it is referenced by a protected foreign key"
                        )
                    )
            except Program.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Program with ID {program_id} does not exist")
                )

        self.stdout.write(self.style.SUCCESS("Remove stale programs complete"))
