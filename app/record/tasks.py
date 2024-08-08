import os
import re
import signal
from datetime import timedelta

import pytz
import requests
from celery import shared_task
from celery_once import QueueOnce
from django.conf import settings
from django.db.models import DateTimeField, ExpressionWrapper, F, Q
from django.utils import timezone
from guide.models import Program

from .models import Recorded, RecordRule


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


def create_recording_task(program_id):
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

    # 録画ファイルのパスを設定
    file_path = generate_unique_filename(
        settings.RECORDED_PATH, program.title, "ts", program.start_at
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
    return


"""
@shared_task
def record_program(program_id):
    try:
        # プログラムをIDで取得
        program = Program.objects.get(id=program_id)
    except Program.DoesNotExist:
        return f"Program with ID {program_id} does not exist."

    # 開始時点で終了済みのプログラムを無視
    if program.is_past:
        return f"Program {program.title} has already ended."

    # 開始時点でstart_atが1分以上後のプログラムを無視
    now = timezone.now()
    if program.start_at > now + timedelta(minutes=1):
        return f"Program {program.title} starts in more than 1 minute."

    # サービスIDを取得
    try:
        service_id = get_service_id(program)
    except Exception as e:
        return str(e)

    # 録画プロセスのチェック
    recent_time = timezone.now() - timedelta(seconds=3)
    if Recorded.objects.filter(program=program, last_updated_at__gte=recent_time).exists():
        return f"Recording process for program {program.title} is already running."

    # 録画ファイルのパスを設定
    file_path = generate_unique_filename(settings.RECORDED_PATH, program.title, "ts")

    # APIのエンドポイントを設定から取得
    stream_url = f"{settings.MIRAKURUN_API}/services/{service_id}/stream"

    # ストリーミングデータを取得
    try:
        response = requests.get(stream_url, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Failed to start recording of program {program.title}: {e}"

    # 録画オブジェクトを作成
    recorded = Recorded.objects.create(
        program=program,
        file=file_path,
        started_at=timezone.now(),
        last_updated_at=timezone.now(),
        is_recording=True
    )

    # 録画を開始
    try:
        with open(file_path, 'wb') as file:
            update_interval = timedelta(seconds=1)  # DB更新の間隔を1秒に設定
            next_update_time = timezone.now() + update_interval
            end_time = program.end_at + timedelta(seconds=3)  # 終了時刻に3秒追加
            refresh_interval = timedelta(seconds=5)  # refresh_from_dbの間隔を5秒に設定
            next_refresh_time = timezone.now() + refresh_interval

            chunk_size = 188 * 40  # 188バイトのパケットの40倍、7520バイトに設定

            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)

                current_time = timezone.now()

                # 定期的にプログラム情報を更新
                if current_time >= next_refresh_time:
                    program.refresh_from_db()
                    end_time = program.end_at + timedelta(seconds=3)
                    next_refresh_time = current_time + refresh_interval

                # プログラムが終了しているかチェック
                if current_time >= end_time:
                    break

                # 定期的にlast_updated_atを更新
                if current_time >= next_update_time:
                    recorded.last_updated_at = current_time
                    recorded.save(update_fields=['last_updated_at'])
                    next_update_time = current_time + update_interval

            # 録画の終了時刻を記録
            recorded.ended_at = timezone.now()
            recorded.is_recording = False
            recorded.save(update_fields=['ended_at', 'is_recording', 'last_updated_at'])

            return f"Recording of program {program.title} completed successfully."

    except Exception as e:
        # ループ中にエラーが発生した場合、録画ファイルを保持し、エラーメッセージを返す
        recorded.ended_at = timezone.now()
        recorded.is_recording = False
        recorded.save(update_fields=['ended_at', 'is_recording', 'last_updated_at'])
        return f"An error occurred during recording of program {program.title}: {e}"
"""


@shared_task
def record_program(recorded_id):
    interrupted = False

    def signal_handler(signal, frame):
        nonlocal interrupted
        interrupted = True
        print("SIGINT received. Exiting gracefully...")

    # SIGINTのシグナルハンドラーを設定
    signal.signal(signal.SIGINT, signal_handler)

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
    now = timezone.now()

    # 現在時刻から5秒以内に開始し、終了していないプログラムを取得
    upcoming_programs = Program.objects.annotate(
        calculated_end_at=ExpressionWrapper(
            F("start_at") + F("duration"), output_field=DateTimeField()
        )
    ).filter(start_at__lte=now + timedelta(seconds=5), calculated_end_at__gt=now)

    for program in upcoming_programs:
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

            # デバッグ用出力
            # print(f"Checking program {program.id} against rule {rule.id}")
            # print(f"Conditions: {conditions}")

            # すべての条件が空の場合はすべてのプログラムを録画対象とする
            if (
                conditions == Q()
                or Program.objects.filter(id=program.id).filter(conditions).exists()
            ):
                # print(f"Recording program {program.id} based on rule {rule.id}")
                create_recording_task(program.id)
                break  # マッチするルールが見つかったら次のプログラムへ

    return "Recording tasks have been started based on the rules."
