from django.urls import path, include
from rest_framework.routers import DefaultRouter

from hardware.views import (
    AudioDataViewSet,
    HardWareDeviceViewSet,
    Text2SpeechViewSet,
    VideoDataViewSet,
)

router = DefaultRouter()

router.register(r"audio", AudioDataViewSet, basename="")

urlpatterns = [
    path(
        "register/",
        HardWareDeviceViewSet.as_view(
            {"get": "list", "post": "create", "put": "update"}
        ),
        name="hardware",
    ),
    # path(
    #     "audio/",
    #     AudioDataViewSet.as_view({"get": "retrieve", "post": "create"}),
    #     name="audio_data",
    # ),
    path(
        "video/",
        VideoDataViewSet.as_view({"get": "retrieve", "post": "create"}),
        name="video_data",
    ),
    path(
        "speech/",
        Text2SpeechViewSet.as_view({"get": "list", "post": "get_text_to_speech"}),
        name="text2speech",
    ),
    path("", include(router.urls)),
]
