from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from hardware.models import AudioData, VideoData


@admin.register(AudioData)
class AudioDataAdmin(ImportExportModelAdmin):
    list_display = ("id", "sequence_index", "text", "audio_file", "start_time", "end_time")
    search_fields = ("uid", "text")


@admin.register(VideoData)
class VideoDataAdmin(ImportExportModelAdmin):
    list_display = ("id", "video_file")
    search_fields = ("uid", "video_file")
