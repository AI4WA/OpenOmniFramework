from django.urls import include, path
from rest_framework.routers import DefaultRouter

from hardware.views import (
    AudioDataViewSet,
    HardWareDeviceViewSet,
    Text2SpeechViewSet,
    VideoDataViewSet,
)

router = DefaultRouter()

router.register(r"audio", AudioDataViewSet, basename="")
router.register(r"video", VideoDataViewSet, basename="")

urlpatterns = [
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
]
