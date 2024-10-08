from datetime import datetime, timedelta

import pytz
from guide.models import Program


def apply_functions_to_dict(data, functions):
    """
    辞書のキーとバリューに対して指定された関数を適用する
    """

    def apply_functions(value):
        for func in functions:
            value = func(value)
        return value

    return {apply_functions(key): apply_functions(value) for key, value in data.items()}


def sanitize_filename(filename):
    """
    Linuxのファイル名で許容されない文字を適切に処理する関数
    """
    prohibited_characters = {
        "/": "_",  # スラッシュをアンダースコアに置き換え
        "\0": "_",  # NULL文字をアンダースコアに置き換え
    }

    # 変換テーブルの作成
    translation_table = str.maketrans(prohibited_characters)

    # 文字列の変換
    sanitized_filename = filename.translate(translation_table)

    return sanitized_filename


def convert_enclosed_characters(text):
    enclosed_characters_convert_table = {
        "\U0001f14a": "[HV]",
        "\U0001f13f": "[P]",
        "\U0001f14c": "[SD]",
        "\U0001f146": "[W]",
        "\U0001f14b": "[MV]",
        "\U0001f210": "[手]",
        "\U0001f211": "[字]",
        "\U0001f212": "[双]",
        "\U0001f213": "[デ]",
        "\U0001f142": "[S]",
        "\U0001f214": "[二]",
        "\U0001f215": "[多]",
        "\U0001f216": "[解]",
        "\U0001f14d": "[SS]",
        "\U0001f131": "[B]",
        "\U0001f13d": "[N]",
        "\U0001f217": "[天]",
        "\U0001f218": "[交]",
        "\U0001f219": "[映]",
        "\U0001f21a": "[無]",
        "\U0001f21b": "[料]",
        "\u26bf": "[鍵]",
        "\U0001f21c": "[前]",
        "\U0001f21d": "[後]",
        "\U0001f21e": "[再]",
        "\U0001f21f": "[新]",
        "\U0001f220": "[初]",
        "\U0001f221": "[終]",
        "\U0001f222": "[生]",
        "\U0001f223": "[販]",
        "\U0001f224": "[声]",
        "\U0001f225": "[吹]",
        "\U0001f14e": "[PPV]",
        "\u3299": "[秘]",
        "\U0001f200": "[ほか]",
    }

    for key, value in enclosed_characters_convert_table.items():
        text = text.replace(key, value)

    return text


def convert_fullwidth_to_halfwidth(text):
    result = []
    for char in text:
        code = ord(char)
        # 全角英数字および記号の範囲
        if 0xFF01 <= code <= 0xFF5E:
            # 半角に変換
            result.append(chr(code - 0xFEE0))
        elif 0x3000 == code:
            # 全角スペースを半角スペースに変換
            result.append(chr(0x0020))
        else:
            result.append(char)
    return "".join(result)


def create_or_update_program(data):
    # relatedItemsにsharedが存在するかどうかをチェック
    related_items = data.get("relatedItems", [])
    has_shared = any(item["type"] == "shared" for item in related_items)

    if has_shared:
        # sharedアイテムがプログラムのservice_idとevent_idに一致するかをチェック
        match_found = any(
            item["type"] == "shared"
            and item["serviceId"] == data.get("serviceId")
            and item["eventId"] == data.get("eventId")
            for item in related_items
        )
        if not match_found:
            # 一致するsharedアイテムが存在しない場合はプログラムを無視
            return None, False

    # Programの作成または更新
    start_at_timestamp = data.get("startAt") / 1000
    tokyo_tz = pytz.timezone("Asia/Tokyo")
    start_at = datetime.fromtimestamp(
        start_at_timestamp, tz=tokyo_tz
    )  # タイムゾーンを追加

    title = data.get("name", "")
    title = sanitize_filename(title)
    title = convert_enclosed_characters(title)
    title = convert_fullwidth_to_halfwidth(title)

    functions = [convert_enclosed_characters, convert_fullwidth_to_halfwidth]
    extended_info = data.get("extended", {})
    extended_info = apply_functions_to_dict(extended_info, functions)

    description = data.get("description", "")
    description = convert_enclosed_characters(description)
    description = convert_fullwidth_to_halfwidth(description)

    program, created = Program.objects.update_or_create(
        program_id=data.get("id"),
        defaults={
            "event_id": data.get("eventId"),
            "service_id": data.get("serviceId"),
            "network_id": data.get("networkId"),
            "start_at": start_at,
            "duration": timedelta(milliseconds=data.get("duration")),
            "is_free": data.get("isFree"),
            "extended_info": extended_info,
            "genres": data.get("genres", []),
            "audio_infos": data.get("audios", []),
            "related_items": data.get("relatedItems", []),
            "title": title,
            "description": description,
            "video_info": data.get("video", {}),
            "pf_flag": data.get("_pf", False),
        },
    )

    return program, created
