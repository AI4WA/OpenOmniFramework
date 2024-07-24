from django.urls import include, path
from rest_framework.routers import DefaultRouter

from hardware.views import (
    AudioDataViewSet,
    HardWareDeviceViewSet,
    Text2SpeechViewSet,
    VideoDataViewSet,
    ai_audio,
    client_audio,
    client_video,
    storage_solution,
    upload_file,
    list_files,
    download_file_link
)

router = DefaultRouter()

router.register(r"audio", AudioDataViewSet, basename="")
router.register(r"video", VideoDataViewSet, basename="")

urlpatterns = [
    path("storage_solution/", storage_solution, name="storage_solution"),
    path("upload_file/", upload_file, name="upload_file"),
    path("list_files/", list_files, name="list_files"),
    path("download_file_link/", download_file_link, name="download_file_link"),
    path(
        "register/",
        HardWareDeviceViewSet.as_view(
            {"get": "list", "post": "create", "put": "update"}
        ),
        name="hardware",
    ),
    path(
        "speech/",
        Text2SpeechViewSet.as_view({"get": "list", "post": "get_text_to_speech"}),
        name="text2speech",
    ),
    path("", include(router.urls)),
    path("client_audio/<int:audio_id>", client_audio, name="client_audio"),
    path("client_video/<int:conversation_id>", client_video, name="client_video"),
    path("ai_audio/<int:audio_id>", ai_audio, name="ai_audio"),
]
