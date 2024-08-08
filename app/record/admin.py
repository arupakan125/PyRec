from django.contrib import admin

from .models import EncodeTask, Recorded, RecordRule

# Register your models here.


class RecordRuleAdmin(admin.ModelAdmin):
    list_display = ("keyword", "service_id", "is_enable", "recording_path")
    list_filter = ("is_enable", "service_id")
    search_fields = ("keyword",)
    ordering = ("-is_enable", "service_id")
    list_editable = ("is_enable", "recording_path")
    actions = ["enable_selected", "disable_selected"]

    def enable_selected(self, request, queryset):
        queryset.update(is_enable=True)

    enable_selected.short_description = "Enable selected recording rules"

    def disable_selected(self, request, queryset):
        queryset.update(is_enable=False)

    disable_selected.short_description = "Disable selected recording rules"


class RecordedAdmin(admin.ModelAdmin):
    list_display = (
        "program",
        "file",
        "started_at",
        "last_updated_at",
        "ended_at",
        "is_recording",
    )
    search_fields = ("program__title", "file")
    list_filter = ("is_recording", "started_at", "ended_at", "program__service_id")
    readonly_fields = (
        "program",
        "file",
        "started_at",
        "last_updated_at",
        "ended_at",
        "is_recording",
    )
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "program",
                    "file",
                    "started_at",
                    "last_updated_at",
                    "ended_at",
                    "is_recording",
                )
            },
        ),
    )


class EncodeTaskAdmin(admin.ModelAdmin):
    list_display = (
        "recorded",
        "file",
        "encoder_path",
        "is_executed",
        "started_at",
        "ended_at",
    )
    list_filter = ("is_executed", "started_at", "ended_at")
    search_fields = (
        "recorded__name",
        "encoder_path",
    )
    readonly_fields = ("started_at", "ended_at", "error_message")
    ordering = ("-started_at",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "recorded",
                    "file",
                    "encoder_path",
                    "encoding_path",
                    "is_executed",
                )
            },
        ),
        ("Timestamps", {"fields": ("started_at", "ended_at")}),
        ("Errors", {"fields": ("error_message",)}),
    )


admin.site.register(EncodeTask, EncodeTaskAdmin)
admin.site.register(RecordRule, RecordRuleAdmin)
admin.site.register(Recorded, RecordedAdmin)
