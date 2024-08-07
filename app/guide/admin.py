from datetime import datetime

import pytz
from django.conf import settings
from django.contrib import admin
from django.db.models import DateTimeField, ExpressionWrapper, F
from django.utils import timezone
from django.utils.dateformat import format
from django.utils.translation import gettext_lazy as _

from .models import AudioInfo, Genre, Program, RelatedItem, VideoInfo


# Register your models here.
@admin.register(VideoInfo)
class VideoInfoAdmin(admin.ModelAdmin):
    list_display = ('video_type', 'resolution',
                    'stream_content', 'component_type')
    search_fields = ('video_type', 'resolution')


@admin.register(AudioInfo)
class AudioInfoAdmin(admin.ModelAdmin):
    list_display = ('component_type', 'component_tag',
                    'is_main', 'sampling_rate')
    search_fields = ('component_type', 'languages')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('level1', 'level2', 'user_nibble1', 'user_nibble2')
    list_filter = ('level1', 'level2')
    search_fields = ('user_nibble1', 'user_nibble2')


@admin.register(RelatedItem)
class RelatedItemAdmin(admin.ModelAdmin):
    list_display = ('item_type', 'network_id', 'service_id', 'event_id')
    search_fields = ('item_type', 'network_id', 'service_id', 'event_id')


class IsAiringFilter(admin.SimpleListFilter):
    title = _('Currently Airing')
    parameter_name = 'is_airing'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        now = datetime.now(pytz.timezone('Asia/Tokyo'))
        queryset = queryset.annotate(
            end_time=ExpressionWrapper(
                F('start_at') + F('duration'), output_field=DateTimeField())
        )
        if self.value() == 'yes':
            return queryset.filter(start_at__lte=now, end_time__gte=now)
        elif self.value() == 'no':
            return queryset.exclude(start_at__lte=now, end_time__gte=now)
        return queryset


class IsPastFilter(admin.SimpleListFilter):
    title = _('Past Programs')
    parameter_name = 'is_past'

    def lookups(self, request, model_admin):
        return (
            ('yes', _('Yes')),
            ('no', _('No')),
        )

    def queryset(self, request, queryset):
        now = datetime.now(pytz.timezone('Asia/Tokyo'))
        queryset = queryset.annotate(
            end_time=ExpressionWrapper(
                F('start_at') + F('duration'), output_field=DateTimeField())
        )
        if self.value() == 'yes':
            return queryset.filter(end_time__lte=now)
        elif self.value() == 'no':
            return queryset.filter(end_time__gt=now)
        return queryset


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('program_id', 'title', 'event_id', 'service_id', 'network_id',
                    'start_at', 'end_at_display', 'duration', 'is_airing_display', 'is_past_display')
    list_filter = ('service_id', 'network_id', 'is_free',
                   IsAiringFilter, IsPastFilter, 'start_at')
    search_fields = ('title', 'description', 'program_id',
                     'event_id', 'service_id', 'network_id')
    readonly_fields = ('program_id', 'event_id', 'service_id', 'network_id', 'start_at', 'end_at_display', 'duration', 'is_free', 'extended_info',
                       'title', 'description', 'pf_flag', 'is_airing_display', 'is_past_display', 'video_info', 'audio_infos', 'genres', 'related_items')
    fieldsets = (
        (None, {
            'fields': ('program_id', 'event_id', 'service_id', 'network_id', 'start_at', 'end_at_display', 'duration', 'is_free', 'extended_info', 'title', 'description', 'pf_flag', 'is_airing_display', 'is_past_display')
        }),
        ('関連情報', {
            'fields': ('video_info', 'audio_infos', 'genres', 'related_items')
        }),
    )
    filter_horizontal = ('audio_infos', 'genres', 'related_items')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            end_time=ExpressionWrapper(
                F('start_at') + F('duration'), output_field=DateTimeField())
        )

    def is_airing_display(self, obj):
        return obj.is_airing
    is_airing_display.boolean = True
    is_airing_display.short_description = 'Currently Airing'

    def is_past_display(self, obj):
        return obj.is_past
    is_past_display.boolean = True
    is_past_display.short_description = 'Is Past'

    def end_at_display(self, obj):
        local_end_at = timezone.localtime(obj.end_at)
        date_format = settings.DATE_FORMAT if hasattr(
            settings, 'DATE_FORMAT') else 'N j, Y'
        time_format = settings.TIME_FORMAT if hasattr(
            settings, 'TIME_FORMAT') else 'P'
        return format(local_end_at, f'{date_format}, {time_format}')
    end_at_display.admin_order_field = 'end_time'
    end_at_display.short_description = 'End Time'
