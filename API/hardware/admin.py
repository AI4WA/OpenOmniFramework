from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin

from hardware.models import (
    ContextEmotionDetection,
    DataAudio,
    DataMultiModalConversation,
    DataText,
    DataVideo,
    HardWareDevice,
    Home,
    ResSpeech,
    ResText,
)
from orchestrator.chain.manager import CLUSTERS

# import mark_safe
from django.utils.safestring import mark_safe


class ClusterFilter(admin.SimpleListFilter):
    title = _("Cluster")
    parameter_name = "cluster"

    def lookups(self, request, model_admin):
        return [(cluster, cluster) for cluster in CLUSTERS]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(track_id__startswith=f"T-{self.value()}")
        return queryset


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
        "end_time",
    )
    search_fields = ("uid", "text", "sequence_index")
    list_filter = ("uid", "start_time", "end_time", ClusterFilter)

    @admin.display(description="record_create_time")
    def created_at_seconds(self, obj):
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")

    @admin.display(description="record_update_time")
    def updated_at_seconds(self, obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")

    readonly_fields = ("created_at_seconds", "updated_at_seconds")


@admin.register(DataVideo)
class DataVideoAdmin(ImportExportModelAdmin):
    list_display = ("id", "home", "video_file", "start_time", "end_time")
    search_fields = ("uid", "video_file")
    readonly_fields = ("created_at", "updated_at")
    list_filter = (
        "uid",
        "start_time",
        "end_time",
    )


@admin.register(DataText)
class DataTextAdmin(ImportExportModelAdmin):

    def audio__sequence_index(self, obj):
        return obj.audio.sequence_index

    def audio__uid(self, obj):
        return obj.audio.uid

    list_display = (
        "id",
        "text",
        "audio__sequence_index",
        "audio__uid",
        "model_name",
    )
    search_fields = ("text",)
    readonly_fields = ("created_at", "updated_at")
    list_filter = (
        "model_name",
        "audio__sequence_index",
        "audio__uid",
    )


@admin.register(ResText)
class ResTextAdmin(ImportExportModelAdmin):
    list_display = ("id", "text")
    search_fields = ("text",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(ResSpeech)
class ResSpeechAdmin(ImportExportModelAdmin):
    list_display = ("id", "text2speech_file")
    search_fields = ("text", "text2speech_file")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ContextEmotionDetection)
class ContextEmotionDetectionAdmin(ImportExportModelAdmin):
    list_display = ("id", "result")
    search_fields = ("result", "logs")
    readonly_fields = ("created_at", "updated_at")


@admin.register(DataMultiModalConversation)
class DataMultiModalConversationAdmin(ImportExportModelAdmin):

    # form = DataMultiModalConversationAdminForm

    def audio__time_range(self, obj):
        # format it "%Y-%m-%d %H:%M:%S"
        if obj.audio is None:
            return "No Audio"
        start_time_str = obj.audio.start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = obj.audio.end_time.strftime("%Y-%m-%d %H:%M:%S")
        return f"{start_time_str} - {end_time_str}"

    audio__time_range.short_description = "Time Range: Audio"

    def video__time_range(self, obj):
        if len(obj.video.all()) == 0:
            return "No Video"
        videos = obj.video.all().order_by("start_time")
        # get the first video start time and the last video end time
        start_time_str = videos.first().start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = videos.last().end_time.strftime("%Y-%m-%d %H:%M:%S")
        return f"{start_time_str} - {end_time_str}"

    video__time_range.short_description = "Time Range: Video"

    def play_audio(self, obj):
        if obj.audio is None:
            return "No Audio"

        return mark_safe(
            f'<audio controls name="media"><source src="{obj.audio.url()}" type="audio/mpeg"></audio>'
        )

    def play_video(self, obj):
        if obj.video is None:
            return "No Video"
        return mark_safe(
            f'<video width="320" height="240" controls><source src="{obj.video_url()}" type="video/mp4"></video>'
        )

    def play_res_speech(self, obj):
        if obj.res_speech is None:
            return "No Res Speech"
        return mark_safe(
            f'<audio controls name="media"><source src="{obj.res_speech.url()}" type="audio/mpeg"></audio>'
        )

    def speech_to_text(self, obj):
        if obj.text is None:
            return "No Text"
        return obj.text.text

    def response_text(self, obj):
        if obj.res_text is None:
            return "No Res Text"
        return obj.res_text.text

    list_display = (
        "id",
        "audio__time_range",
        "video__time_range",
        "text",
        "res_text",
        "res_speech",
    )
    exclude = (
        "audio",
        "video",
        "res_speech",
        "res_text",
        "text",
    )
    search_fields = (
        "text__text",
        "res_text__text",
        "track_id",
        "text",
    )
    readonly_fields = (
        "track_id",
        "play_audio",
        "audio__time_range",
        "speech_to_text",
        "play_video",
        "video__time_range",
        "response_text",
        "play_res_speech",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", ClusterFilter)
