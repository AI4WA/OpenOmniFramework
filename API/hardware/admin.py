from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse

# import mark_safe
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportMixin, ImportExportModelAdmin

from authenticate.models import User
from hardware.forms import (
    MultiModalAnnotationForm,
    MultiModalFKEmotionDetectionAnnotationForm,
)
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
from orchestrator.metrics.accuracy_benchmark import AccuracyBenchmark


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


@admin.register(DataMultiModalConversation)
class DataMultiModalConversationAdmin(ImportExportMixin, admin.ModelAdmin):
    import_export_change_list_template = "admin/hardware/conversation/change_list.html"
    form = MultiModalAnnotationForm

    def get_urls(self):
        # the custom urls will be changed when ClusterFilter is changed, how can I implement it?
        urls = super().get_urls()
        custom_urls = [
            path(
                "accuracy_benchmark/",
                self.admin_site.admin_view(self.accuracy_benchmark),
                name="accuracy_benchmark",
            ),
            path(
                "accuracy_detail/",
                self.admin_site.admin_view(self.accuracy_detail),
                name="accuracy_detail",
            ),
        ]
        return custom_urls + urls

    @staticmethod
    def accuracy_benchmark(request):
        # get parameter from request url
        cluster = request.GET.get("cluster", "all")
        benchmark = AccuracyBenchmark(benchmark_cluster=cluster)
        html_content = benchmark.benchmark_run()
        context = {"content": html_content, "benchmark_type": "Accuracy Overall"}
        return render(request, "admin/orchestrator/task/benchmark.html", context)

    @staticmethod
    def accuracy_detail(request):
        cluster = request.GET.get("cluster", "all")
        benchmark = AccuracyBenchmark(benchmark_cluster=cluster)
        html_content = benchmark.detail_run()
        context = {"content": html_content, "benchmark_type": "Accuracy Detail"}
        return render(request, "admin/orchestrator/task/benchmark.html", context)

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
        if obj.video is None or len(obj.video.all()) == 0:
            return "No Video"
        return mark_safe(
            f'<video width="320" height="240" controls><source src="{obj.video_url()}" type="video/mp4"></video>'
        )

    def play_res_speech(self, obj):
        if obj.res_speech is None:
            return "No Response Speech"
        return mark_safe(
            f'<audio controls name="media"><source src="{obj.res_speech.url()}" type="audio/mpeg"></audio>'
        )

    def speech_to_text(self, obj):
        if obj.text is None:
            return "No Text"
        return obj.text.text

    def response_text(self, obj):
        if obj.res_text is None:
            return "No Response Text"
        return obj.res_text.text

    def annotation_records(self, obj):
        annotations = obj.annotations
        if not annotations:
            return "No Annotations"
        """
        Get this presentation into a html like this:

        User: {username}
        Annotation Overall: {annotation_overall}
        Annotation Text Modality: {annotation_text_modality}
        Annotation Audio Modality: {annotation_audio_modality}
        ----
        User: {username}
        ....

        """

        return_html = "<div>"
        return_html += f"<h5>Total Annotator: {len(annotations.items())} </h5>"
        return_html += "<hr>"
        for user_id, annotation in annotations.items():
            user = User.objects.get(pk=user_id)
            return_html += f"<h6>User: {user.username}</h6>"
            return_html += "<ul>"
            for annotation_key, annotation_value in annotation.items():
                return_html += f"<li>{annotation_key}: {annotation_value}</li>"
            return_html += "</ul>"
            return_html += "<hr>"
        return_html += "</div>"
        return mark_safe(return_html)

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
        "annotations",
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
        "annotation_records",
    )
    list_filter = ("created_at", ClusterFilter)

    change_form_template = "admin/hardware/conversation/change_form.html"

    def response_change(self, request, obj):
        if "_saveandnext" in request.POST:
            next_obj = self.get_next_obj(obj)
            if next_obj:
                return HttpResponseRedirect(
                    reverse(
                        "admin:%s_%s_change"
                        % (obj._meta.app_label, obj._meta.model_name),
                        args=[next_obj.pk],
                    )
                )
        return super().response_change(request, obj)

    def get_next_obj(self, obj):
        # Define your logic to get the next object
        next_obj = (
            DataMultiModalConversation.objects.filter(pk__gt=obj.pk)
            .order_by("pk")
            .first()
        )
        return next_obj

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if extra_context is None:
            extra_context = {}

        extra_context["additional_save_buttons"] = [
            {"name": "_saveandnext", "value": "Save and Next"}
        ]

        return super().change_view(request, object_id, form_url, extra_context)

    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        form.current_user = request.user
        return form

    def save_model(self, request, obj, form, change):
        annotation_data = {}
        for key, value in form.cleaned_data.items():
            if key.startswith("annotation_"):
                annotation_data[key] = value

        if not obj.annotations:
            obj.annotations = {}
        current_annotations = obj.annotations.get(request.user.id, {})
        obj.annotations[request.user.id] = {
            **annotation_data,
            **current_annotations,
        }

        super().save_model(request, obj, form, change)


class DataMultiModalConversationFKAdmin(ImportExportModelAdmin):
    """
    All the obj above will be self.multi_modal_conversation
    """

    def audio__time_range(self, obj):
        # format it "%Y-%m-%d %H:%M:%S"
        if obj.multi_modal_conversation.audio is None:
            return "No Audio"
        start_time_str = obj.multi_modal_conversation.audio.start_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        end_time_str = obj.multi_modal_conversation.audio.end_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        return f"{start_time_str} - {end_time_str}"

    audio__time_range.short_description = "Time Range: Audio"

    def video__time_range(self, obj):
        if len(obj.multi_modal_conversation.video.all()) == 0:
            return "No Video"
        videos = obj.multi_modal_conversation.video.all().order_by("start_time")
        # get the first video start time and the last video end time
        start_time_str = videos.first().start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = videos.last().end_time.strftime("%Y-%m-%d %H:%M:%S")
        return f"{start_time_str} - {end_time_str}"

    video__time_range.short_description = "Time Range: Video"

    def play_audio(self, obj):
        if obj.multi_modal_conversation.audio is None:
            return "No Audio"

        return mark_safe(
            f'<audio controls name="media">'
            f'<source src="{obj.multi_modal_conversation.audio.url()}" type="audio/mpeg"></audio>'
        )

    def play_video(self, obj):
        if (
            obj.multi_modal_conversation.video is None
            or len(obj.multi_modal_conversation.video.all()) == 0
        ):
            return "No Video"
        return mark_safe(
            f'<video width="320" height="240" controls>'
            f'<source src="{obj.multi_modal_conversation.video_url()}" type="video/mp4"></video>'
        )

    def play_res_speech(self, obj):
        if obj.multi_modal_conversation.res_speech is None:
            return "No Response Speech"
        return mark_safe(
            f'<audio controls name="media">'
            f'<source src="{obj.multi_modal_conversation.res_speech.url()}" type="audio/mpeg"></audio>'
        )

    def speech_to_text(self, obj):
        if obj.multi_modal_conversation.text is None:
            return "No Text"
        return obj.multi_modal_conversation.text.text

    def response_text(self, obj):
        if obj.multi_modal_conversation.res_text is None:
            return "No Response Text"
        return obj.multi_modal_conversation.res_text.text

    def annotation_records(self, obj):
        annotations = obj.annotations
        if not annotations:
            return "No Annotations"
        """
        Get this presentation into a html like this:

        User: {username}
        Annotation Overall: {annotation_overall}
        Annotation Text Modality: {annotation_text_modality}
        Annotation Audio Modality: {annotation_audio_modality}
        ----
        User: {username}
        ....

        """

        return_html = "<div>"
        return_html += f"<h5>Total Annotator: {len(annotations.items())} </h5>"
        return_html += "<hr>"
        for user_id, annotation in annotations.items():
            user = User.objects.get(pk=user_id)
            return_html += f"<h6>User: {user.username}</h6>"
            return_html += "<ul>"
            for annotation_key, annotation_value in annotation.items():
                return_html += f"<li>{annotation_key}: {annotation_value}</li>"
            return_html += "</ul>"
            return_html += "<hr>"
        return_html += "</div>"
        return mark_safe(return_html)

    list_display = (
        "id",
        "audio__time_range",
        "video__time_range",
    )
    exclude = (
        "audio",
        "video",
        "text",
        "annotations",
    )
    search_fields = (
        "text__text",
        "res_text__text",
        "track_id",
        "text",
    )
    readonly_fields = (
        # "track_id",
        "play_audio",
        "audio__time_range",
        "speech_to_text",
        "play_video",
        "video__time_range",
        "response_text",
        "play_res_speech",
        "created_at",
        "updated_at",
        "annotation_records",
    )
    list_filter = ("created_at", ClusterFilter)

    change_form_template = "admin/hardware/conversation/change_form.html"

    def response_change(self, request, obj):
        if "_saveandnext" in request.POST:
            next_obj = self.get_next_obj(obj)
            if next_obj:
                return HttpResponseRedirect(
                    reverse(
                        "admin:%s_%s_change"
                        % (
                            obj._meta.app_label,
                            obj._meta.model_name,
                        ),
                        args=[next_obj.pk],
                    )
                )
        return super().response_change(request, obj)

    def get_next_obj(self, obj):
        # Define your logic to get the next object
        # use self model to get the next object
        obj_model = obj.__class__
        next_obj = obj_model.objects.filter(pk__gt=obj.pk).order_by("pk").first()
        return next_obj

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if extra_context is None:
            extra_context = {}

        extra_context["additional_save_buttons"] = [
            {"name": "_saveandnext", "value": "Save and Next"}
        ]

        return super().change_view(request, object_id, form_url, extra_context)

    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)
        form.current_user = request.user
        return form

    def save_model(self, request, obj, form, change):
        annotation_data = {}
        for key, value in form.cleaned_data.items():
            if key.startswith("annotation_"):
                annotation_data[key] = value

        if not obj.annotations:
            obj.annotations = {}
        current_annotations = obj.annotations.get(request.user.id, {})
        obj.annotations[request.user.id] = {
            **annotation_data,
            **current_annotations,
        }

        super().save_model(request, obj, form, change)


@admin.register(ContextEmotionDetection)
class ContextEmotionDetectionAdmin(DataMultiModalConversationFKAdmin):
    form = MultiModalFKEmotionDetectionAnnotationForm

    def emotion_overall(self, obj):
        return obj.result.get("M", "No Result")

    emotion_overall.short_description = "Emotion Overall"

    def emotion_text_modality(self, obj):
        return obj.result.get("T", "No Result")

    emotion_text_modality.short_description = "Emotion Text Modality"

    def emotion_audio_modality(self, obj):
        return obj.result.get("A", "No Result")

    emotion_audio_modality.short_description = "Emotion Audio Modality"

    def emotion_video_modality(self, obj):
        return obj.result.get("V", "No Result")

    emotion_video_modality.short_description = "Emotion Video Modality"

    list_display = DataMultiModalConversationFKAdmin.list_display + ("emotion_overall",)
    readonly_fields = (
        "emotion_overall",
        "emotion_text_modality",
        "emotion_audio_modality",
        "emotion_video_modality",
    ) + DataMultiModalConversationFKAdmin.readonly_fields
    exclude = DataMultiModalConversationFKAdmin.exclude + (
        "result",
        "logs",
        "multi_modal_conversation",
    )
