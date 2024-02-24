from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from hardware.models import AudioData


@admin.register(AudioData)
class AudioDataAdmin(ImportExportModelAdmin):
    list_display = ("id", "sequence_index", "text", "audio_file", "start_time", "end_time")
    search_fields = ("uid", "text")
