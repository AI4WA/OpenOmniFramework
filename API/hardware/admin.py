from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from hardware.models import AudioData, VideoData, HardWareDevice


@admin.register(HardWareDevice)
class HardWareDeviceAdmin(ImportExportModelAdmin):
    list_display = ("id", "mac_address", "device_name", "device_type", "created_at", "updated_at")
    search_fields = ("mac_address", "device_name", "device_type")
    list_filter = ("device_type",)


@admin.register(AudioData)
class AudioDataAdmin(ImportExportModelAdmin):
    list_display = ("id", "sequence_index", "text", "audio_file", "start_time", "translation_in_seconds")
    search_fields = ("uid", "text")

    @admin.display(description="record_create_time")
    def created_at_seconds(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    @admin.display(description="record_update_time")
    def updated_at_seconds(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    readonly_fields = ("created_at_seconds", "updated_at_seconds")


@admin.register(VideoData)
class VideoDataAdmin(ImportExportModelAdmin):
    list_display = ("id", "video_file")
    search_fields = ("uid", "video_file")
    readonly_fields = ("created_at", "updated_at")
