from datetime import datetime, timedelta

import pytz
from django.db import models

# Create your models here.


# models.py

class GenreLevel1(models.IntegerChoices):
    NEWS_REPORT = 0x0, 'ニュース/報道'
    SPORTS = 0x1, 'スポーツ'
    INFORMATION_WIDE_SHOW = 0x2, '情報/ワイドショー'
    DRAMA = 0x3, 'ドラマ'
    MUSIC = 0x4, '音楽'
    VARIETY = 0x5, 'バラエティ'
    MOVIE = 0x6, '映画'
    ANIME_SPECIAL_EFFECTS = 0x7, 'アニメ/特撮'
    DOCUMENTARY_EDUCATION = 0x8, 'ドキュメンタリー/教養'
    THEATER_PERFORMANCE = 0x9, '劇場/公演'
    HOBBY_EDUCATION = 0xA, '趣味/教育'
    WELFARE = 0xB, '福祉'
    RESERVED_1 = 0xC, '予備'
    RESERVED_2 = 0xD, '予備'
    EXTENSION = 0xE, '拡張'
    OTHERS = 0xF, 'その他'


class GenreLevel2(models.IntegerChoices):
    # ニュース/報道
    GENERAL_NEWS = 0x00, '定時・総合'
    WEATHER = 0x01, '天気'
    FEATURE_DOCUMENTARY = 0x02, '特集・ドキュメント'
    POLITICS = 0x03, '政治・国会'
    ECONOMY = 0x04, '経済・市況'
    OVERSEAS = 0x05, '海外・国際'
    COMMENTARY = 0x06, '解説'
    DISCUSSION = 0x07, '討論・会談'
    SPECIAL_NEWS = 0x08, '報道特番'
    LOCAL_NEWS = 0x09, 'ローカル・地域'
    TRAFFIC = 0x0A, '交通'
    OTHER_NEWS = 0x0F, 'その他'

    # スポーツ
    SPORTS_NEWS = 0x10, 'スポーツニュース'
    BASEBALL = 0x11, '野球'
    SOCCER = 0x12, 'サッカー'
    GOLF = 0x13, 'ゴルフ'
    OTHER_BALL_SPORTS = 0x14, 'その他の球技'
    SUMO_WRESTLING = 0x15, '相撲・格闘技'
    OLYMPICS = 0x16, 'オリンピック・国際大会'
    MARATHON = 0x17, 'マラソン・陸上・水泳'
    MOTOR_SPORTS = 0x18, 'モータースポーツ'
    MARINE_SPORTS = 0x19, 'マリン・ウィンタースポーツ'
    COMPETITION = 0x1A, '競馬・公営競技'
    OTHER_SPORTS = 0x1F, 'その他'

    # 情報/ワイドショー
    WIDE_SHOW = 0x20, '芸能・ワイドショー'
    FASHION = 0x21, 'ファッション'
    LIVING = 0x22, '暮らし・住まい'
    HEALTH = 0x23, '健康・医療'
    SHOPPING = 0x24, 'ショッピング・通販'
    GOURMET = 0x25, 'グルメ・料理'
    EVENTS = 0x26, 'イベント'
    PROGRAM_INFO = 0x27, '番組紹介・お知らせ'
    OTHER_INFORMATION = 0x2F, 'その他'

    # ドラマ
    DOMESTIC_DRAMA = 0x30, '国内ドラマ'
    FOREIGN_DRAMA = 0x31, '海外ドラマ'
    PERIOD_DRAMA = 0x32, '時代劇'
    OTHER_DRAMA = 0x3F, 'その他'

    # 音楽
    DOMESTIC_ROCK_POP = 0x40, '国内ロック・ポップス'
    FOREIGN_ROCK_POP = 0x41, '海外ロック・ポップス'
    CLASSICAL_OPERA = 0x42, 'クラシック・オペラ'
    JAZZ_FUSION = 0x43, 'ジャズ・フュージョン'
    ENKA_POPULAR = 0x44, '歌謡曲・演歌'
    LIVE_CONCERT = 0x45, 'ライブ・コンサート'
    RANKING_REQUEST = 0x46, 'ランキング・リクエスト'
    KARAOKE = 0x47, 'カラオケ・のど自慢'
    FOLK_NATIONAL = 0x48, '民謡・邦楽'
    CHILDREN = 0x49, '童謡・キッズ'
    FOLK_WORLD = 0x4A, '民族音楽・ワールドミュージック'
    OTHER_MUSIC = 0x4F, 'その他'

    # バラエティ
    QUIZ = 0x50, 'クイズ'
    GAME = 0x51, 'ゲーム'
    TALK_VARIETY = 0x52, 'トークバラエティ'
    COMEDY = 0x53, 'お笑い・コメディ'
    MUSIC_VARIETY = 0x54, '音楽バラエティ'
    TRAVEL_VARIETY = 0x55, '旅バラエティ'
    COOKING_VARIETY = 0x56, '料理バラエティ'
    OTHER_VARIETY = 0x5F, 'その他'

    # 映画
    WESTERN_MOVIE = 0x60, '洋画'
    JAPANESE_MOVIE = 0x61, '邦画'
    ANIME_MOVIE = 0x62, 'アニメ'
    OTHER_MOVIE = 0x6F, 'その他'

    # アニメ/特撮
    DOMESTIC_ANIME = 0x70, '国内アニメ'
    FOREIGN_ANIME = 0x71, '海外アニメ'
    SPECIAL_EFFECTS = 0x72, '特撮'
    OTHER_ANIME = 0x7F, 'その他'

    # ドキュメンタリー/教養
    SOCIETY = 0x80, '社会・時事'
    HISTORY = 0x81, '歴史・紀行'
    NATURE = 0x82, '自然・動物・環境'
    SCIENCE_MEDICINE = 0x83, '宇宙・科学・医学'
    CULTURE = 0x84, 'カルチャー・伝統文化'
    LITERATURE = 0x85, '文学・文芸'
    SPORTS_EDUCATION = 0x86, 'スポーツ'
    GENERAL_DOCUMENTARY = 0x87, 'ドキュメンタリー全般'
    INTERVIEW_DISCUSSION = 0x88, 'インタビュー・討論'
    OTHER_DOCUMENTARY = 0x8F, 'その他'

    # 劇場/公演
    MODERN_DRAMA = 0x90, '現代劇・新劇'
    MUSICAL = 0x91, 'ミュージカル'
    DANCE_BALLET = 0x92, 'ダンス・バレエ'
    RAKUGO = 0x93, '落語・演芸'
    CLASSIC_OPERA = 0x94, '歌舞伎・古典'
    OTHER_STAGE = 0x9F, 'その他'

    # 拡張
    BS = 0xE0, 'BS/地上デジタル放送用番組付属情報'
    BAND_CS = 0xE1, '広帯域 CS デジタル放送用拡張'
    SERVER_PROGRAM_INFO = 0xE2, 'サーバー型番組付属情報'
    IP_PROGRAM_INFO = 0xE3, 'IP 放送用番組付属情報'
    OTHER_EXTENSION = 0xEF, 'その他'

    # その他
    OTHER = 0xFF, 'その他'


class VideoType(models.TextChoices):
    MPEG2 = 'mpeg2', 'MPEG-2'
    H264 = 'h.264', 'H.264'
    H265 = 'h.265', 'H.265'


class VideoResolution(models.TextChoices):
    P240 = '240p', '240p'
    I480 = '480i', '480i'
    P480 = '480p', '480p'
    P720 = '720p', '720p'
    I1080 = '1080i', '1080i'
    P1080 = '1080p', '1080p'
    P2160 = '2160p', '2160p'
    P4320 = '4320p', '4320p'


class AudioSamplingRate(models.IntegerChoices):
    RATE_16000 = 16000, '16 kHz'
    RATE_22050 = 22050, '22.05 kHz'
    RATE_24000 = 24000, '24 kHz'
    RATE_32000 = 32000, '32 kHz'
    RATE_44100 = 44100, '44.1 kHz'
    RATE_48000 = 48000, '48 kHz'


class AudioComponentType(models.IntegerChoices):
    RESERVED = 0b00000, '将来使用のためリザーブ'
    MONO = 0b00001, '1/0モード（シングルモノ）'
    DUAL_MONO = 0b00010, '1/0+1/0モード（デュアルモノ）'
    STEREO = 0b00011, '2/0モード（ステレオ）'
    MODE_2_1 = 0b00100, '2/1モード'
    MODE_3_0 = 0b00101, '3/0モード'
    MODE_2_2 = 0b00110, '2/2モード'
    MODE_3_1 = 0b00111, '3/1モード'
    MODE_3_2 = 0b01000, '3/2モード'
    MODE_3_2_LFE = 0b01001, '3/2＋LFEモード（3/2.1モード）'
    MODE_3_3_1 = 0b01010, '3/3.1モード'
    MODE_2_0_2_0 = 0b01011, '2/0/0-2/0/2-0.1モード'
    MODE_5_1 = 0b01100, '5/2.1モード'
    MODE_3_2_2_1 = 0b01101, '3/2/2.1モード'
    MODE_2_0_0_3 = 0b01110, '2/0/0-3/0/2-0.1モード'
    MODE_0_2_0_3 = 0b01111, '0/2/0-3/0/2-0.1モード'
    MODE_2_0_0_2_2_3 = 0b10000, '2/0/0-3/2/3-0.2モード'
    MODE_3_3_5 = 0b10001, '3/3/5-2/3-3/0/0.2モード'
    RESERVED_2 = 0b10010, '将来使用のためリザーブ'
    RESERVED_3 = 0b11111, '将来使用のためリザーブ'


class RelatedItemType(models.TextChoices):
    SHARED = 'shared', 'Shared'
    RELAY = 'relay', 'Relay'
    MOVEMENT = 'movement', 'Movement'


class LanguageChoices(models.TextChoices):
    JPN = 'jpn', 'Japanese'
    ENG = 'eng', 'English'
    DEU = 'deu', 'German'
    FRA = 'fra', 'French'
    ITA = 'ita', 'Italian'
    RUS = 'rus', 'Russian'
    ZHO = 'zho', 'Chinese'
    KOR = 'kor', 'Korean'
    SPA = 'spa', 'Spanish'
    ETC = 'etc', 'Other'


class Program(models.Model):
    program_id = models.BigIntegerField(unique=True)
    event_id = models.BigIntegerField()
    service_id = models.IntegerField()
    network_id = models.IntegerField()
    start_at = models.DateTimeField()
    duration = models.DurationField()
    is_free = models.BooleanField()
    extended_info = models.JSONField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    video_info = models.JSONField(blank=True, null=True)
    audio_infos = models.JSONField(blank=True, null=True)
    genres = models.JSONField(blank=True, null=True)
    related_items = models.JSONField(blank=True, null=True)
    pf_flag = models.BooleanField(blank=True, null=True)

    @property
    def end_at(self):
        return self.start_at + self.duration

    @property
    def is_airing(self):
        now = datetime.now(pytz.timezone('Asia/Tokyo'))
        end_time = self.start_at + self.duration
        return self.start_at <= now < end_time

    @property
    def is_past(self):
        now = datetime.now(pytz.timezone('Asia/Tokyo'))
        return now >= self.end_at

    def __str__(self):
        return self.title
