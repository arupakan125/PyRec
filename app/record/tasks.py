import importlib.util
import os
import re
import signal
import sys
from datetime import timedelta

import pytz
import requests
from celery import shared_task
from celery_once import QueueOnce
from django.conf import settings
from django.db.models import DateTimeField, ExpressionWrapper, F, Q
from django.utils import timezone
from guide.models import Program

from .models import EncodeTask, Recorded, RecordRule


def get_service_id(program):
    # サービスAPIのエンドポイント
    api_url = f"{settings.MIRAKURUN_API}/services/"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        services = response.json()
        # 対応するserviceIdを持つサービスを検索
        for service in services:
            if (
                service["serviceId"] == program.service_id
                and service["networkId"] == program.network_id
            ):
                return service["id"]
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to retrieve service ID: {e}")

    raise Exception("Service ID not found")


def generate_unique_filename(directory, base_name, extension, date):
    # Base name を安全な形式に変換
    safe_base_name = re.sub(r"[^\w\s-]", "", base_name).strip().replace(" ", "_")

    # 日付を指定のタイムゾーンに変換
    date = date.astimezone(pytz.timezone("Asia/Tokyo"))

    # 初回のファイル名生成
    filename = (
        f"{date.strftime('%Y年%m月%d日%H時%M分%S秒')}-{safe_base_name}.{extension}"
    )
    django_path = os.path.join(directory, filename)
    full_path = os.path.join(settings.MEDIA_ROOT, django_path)

    # 重複チェック用のカウンタ
    counter = 1

    # 重複がある限り、ファイル名を変更
    while os.path.exists(full_path):
        filename = f"{date.strftime('%Y年%m月%d日%H時%M分%S秒')}-{safe_base_name}({counter}).{extension}"
        django_path = os.path.join(directory, filename)
        full_path = os.path.join(settings.MEDIA_ROOT, django_path)
        counter += 1

    return django_path


def create_recording_task(program_id, recording_path):
    try:
        program = Program.objects.get(id=program_id)
    except Program.DoesNotExist:
        print(f"Program with ID {program_id} does not exist.")
        return

    if program.is_past:
        print(f"Program {program.title} has already ended.")
        return

    now = timezone.now()
    if program.start_at > now + timedelta(minutes=1):
        print(f"Program {program.title} starts in more than 1 minute.")
        return

    # 録画プロセスのチェック
    recent_time = timezone.now() - timedelta(seconds=10)
    if Recorded.objects.filter(
        program=program, last_updated_at__gte=recent_time
    ).exists():
        # print(f"Recording process for program {program.title} is already running.")
        return

    recording_path = os.path.join(settings.RECORDED_PATH, recording_path)

    # 録画ファイルのパスを設定
    file_path = generate_unique_filename(
        recording_path, program.title, "ts", program.start_at
    )

    # 録画オブジェクトを作成
    recorded = Recorded.objects.create(
        program=program,
        file=file_path,
        started_at=timezone.now(),
        last_updated_at=timezone.now(),
        is_recording=False,
    )

    record_program.delay(recorded.id)
    print(f"Recording task for program {program.title} has been started.")
    return recorded


@shared_task
def record_program(recorded_id):
    interrupted = False

    def signal_handler(signal, frame):
        nonlocal interrupted
        interrupted = True
        print("SIGINT received. Exiting gracefully...")

    # SIGINTのシグナルハンドラーを設定
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        recorded = Recorded.objects.get(id=recorded_id)
        program = recorded.program
    except Recorded.DoesNotExist:
        print("Error: Recorded object does not exist.")
        return f"Recorded object with ID {recorded_id} does not exist."
    except Program.DoesNotExist:
        return f"Program with ID {recorded.program_id} does not exist."

    try:
        service_id = get_service_id(program)
    except Exception as e:
        return str(e)

    file_path = recorded.file.path
    stream_url = f"{settings.MIRAKURUN_API}/services/{service_id}/stream"

    try:
        response = requests.get(stream_url, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Failed to start recording of program {program.title}: {e}"

    directory = os.path.dirname(file_path)

    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory created: {directory}")

    try:
        with open(file_path, "wb") as file:
            update_interval = timedelta(seconds=1)
            next_update_time = timezone.now() + update_interval
            end_time = program.end_at + timedelta(seconds=3)
            refresh_interval = timedelta(seconds=5)
            next_refresh_time = timezone.now() + refresh_interval
            is_started = False

            chunk_size = 144 * 10000

            for chunk in response.iter_content(chunk_size=chunk_size):
                if interrupted:
                    break
                current_time = timezone.now()

                # 番組の開始時刻まで待機
                if not is_started:
                    if current_time >= program.start_at:
                        is_started = True
                    else:
                        continue

                file.write(chunk)

                if current_time >= next_refresh_time:
                    program.refresh_from_db()
                    end_time = program.end_at + timedelta(seconds=5)

                    if program.is_removed:
                        break
                    next_refresh_time = current_time + refresh_interval

                # 番組が終了しているかチェック
                if current_time >= end_time:
                    # Durationが1の時は録画を継続
                    if not program.duration == 1:
                        break

                if current_time >= next_update_time:
                    recorded.last_updated_at = current_time
                    recorded.is_recording = True
                    recorded.save(update_fields=["last_updated_at", "is_recording"])
                    next_update_time = current_time + update_interval

            recorded.ended_at = timezone.now()
            recorded.is_recording = False
            recorded.save(update_fields=["ended_at", "is_recording", "last_updated_at"])

            if interrupted:
                return f"Recording of program {program.title} interrupted and stopped due to shutdown signal."
            if program.is_removed:
                return f"Program {program.title} has been removed and recording has been stopped."
            return f"Recording of program {program.title} completed successfully."

    except Exception as e:
        recorded.ended_at = timezone.now()
        recorded.is_recording = False
        recorded.save(update_fields=["ended_at", "is_recording", "last_updated_at"])
        return f"An error occurred during recording of program {program.title}: {e}"


@shared_task(base=QueueOnce, once={"graceful": True})
def start_recording_based_on_rules():
    def get_rules_match_program(program):
        rules = []
        for rule in RecordRule.objects.filter(is_enable=True):
            conditions = Q()
            if rule.keyword:
                conditions &= (
                    Q(title__icontains=rule.keyword)
                    | Q(description__icontains=rule.keyword)
                    | Q(extended_info__icontains=rule.keyword)
                )
            if rule.service_id:
                conditions &= Q(service_id=rule.service_id)

            if (
                conditions == Q()
                or Program.objects.filter(id=program.id).filter(conditions).exists()
            ):
                rules.append(rule)
        return rules

    now = timezone.now()

    # 現在時刻から5秒以内に開始し、終了していないプログラムを取得
    upcoming_programs = Program.objects.annotate(
        calculated_end_at=ExpressionWrapper(
            F("start_at") + F("duration"), output_field=DateTimeField()
        )
    ).filter(start_at__lte=now + timedelta(seconds=5), calculated_end_at__gt=now)

    for program in upcoming_programs:
        rules = get_rules_match_program(program)
        if rules:
            recorded = create_recording_task(program.id, rules[0].recording_path)
            if not recorded:
                continue
            for rule in rules:
                EncodeTask.objects.create(
                    recorded=recorded,
                    encoder_path=rule.encoder_path,
                    encoding_path=rule.encoding_path,
                )
    return "Recording tasks have been started based on the rules."


@shared_task(base=QueueOnce, once={"graceful": True})
def encode():
    for task in EncodeTask.objects.filter(is_executed=False):
        if not task.recorded.ended_at:
            continue

        encoding_path = os.path.join(settings.ENCODED_PATH, task.encoding_path)

        # 録画ファイルのパスを設定
        file_path = generate_unique_filename(
            encoding_path,
            task.recorded.program.title,
            "mp4",
            task.recorded.program.start_at,
        )

        task.file = file_path
        task.started_at = timezone.now()
        task.is_executed = True
        task.save(update_fields=["file", "is_executed", "started_at"])

        function_name = "encode"

        encorder_path = os.path.join("record/encode/", task.encoder_path)

        # 関数を呼び出す
        input_file = task.recorded.file.path
        output_file = task.file.path
        try:
            # 動的にモジュールをインポート
            module_name = os.path.splitext(os.path.basename(file_path))[0]
            spec = importlib.util.spec_from_file_location(module_name, encorder_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # 関数を取得
            func = getattr(module, function_name)
            directory = os.path.dirname(output_file)
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Directory created: {directory}")
            task.started_at = timezone.now()
            task.save(update_fields=["is_executed", "started_at"])
            func(input_file, output_file)
            task.ended_at = timezone.now()
            task.save(update_fields=["is_executed", "ended_at"])
            break
        except Exception as e:
            print(f"An error occurred during encoding: {e}")
            task.error_message = str(e)
            task.save(update_fields=["error_message"])
            break
