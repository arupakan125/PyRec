from celery import shared_task  # type: ignore
from celery_once import QueueOnce
from celery_once.tasks import AlreadyQueued
from django.core.management import call_command


@shared_task(base=QueueOnce, once={"graceful": True})
def sync_programs():
    call_command("sync_programs")


@shared_task()
def remove_stale_programs():
    call_command("remove_stale_programs")


@shared_task(base=QueueOnce, once={"graceful": True})
def process_program_events():
    call_command("process_program_events")
