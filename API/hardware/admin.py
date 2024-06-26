from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from hardware.models import (
    DataAudio,
    DataText,
    DataVideo,
    EmotionDetection,
    HardWareDevice,
    Home,
    LLMResponse,
    Text2Speech,
)


@admin.register(Home)
class HomeAdmin(ImportExportModelAdmin):
    list_display = ("id", "user", "name")
    search_fields = ("name", "address")
    list_filter = ("user",)


@admin.register(HardWareDevice)
class HardWareDeviceAdmin(ImportExportModelAdmin):
    list_display = (
        "id",
        "home",
        "mac_address",
        "device_name",
        "device_type",
        "created_at",
        "updated_at",
    )
    search_fields = ("mac_address", "device_name", "device_type")
    list_filter = ("device_type",)


@admin.register(DataAudio)
class DataAudioAdmin(ImportExportModelAdmin):
    list_display = (
        "id",
        "home",
        "sequence_index",
        "audio_file",
        "start_time",
    )
    search_fields = ("uid", "text")

    @admin.display(description="record_create_time")
    def created_at_seconds(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    @admin.display(description="record_update_time")
    def updated_at_seconds(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    readonly_fields = ("created_at_seconds", "updated_at_seconds")


@admin.register(DataVideo)
class DataVideoAdmin(ImportExportModelAdmin):
    list_display = ("id", "home", "video_file", "video_record_minute")
    search_fields = ("uid", "video_file")
    readonly_fields = ("created_at", "updated_at")


@admin.register(DataText)
class DataTextAdmin(ImportExportModelAdmin):
    list_display = ("id", "home", "audio", "text", "pipeline_triggered")
    search_fields = ("text",)
    readonly_fields = ("created_at", "updated_at")
    list_filter = ("pipeline_triggered",)


@admin.register(EmotionDetection)
class EmotionDetectionAdmin(ImportExportModelAdmin):
    list_display = ("id", "home", "result")
    search_fields = ("result", "logs")
    readonly_fields = ("created_at", "updated_at")


@admin.register(LLMResponse)
class LLMResponseAdmin(ImportExportModelAdmin):
    list_display = ("id", "home", "data_text", "result")
    search_fields = ("result", "logs", "messages")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Text2Speech)
class Text2SpeechAdmin(ImportExportModelAdmin):
    list_display = ("id", "text")
    search_fields = ("text", "audio_file")
    filter_fields = ("hardware_device_mac_address",)
    readonly_fields = ("created_at", "updated_at")
