from django.urls import path
from hardware.views import AudioDataViewSet, VideoDataViewSet

urlpatterns = [
    path("audio/", AudioDataViewSet.as_view({"get": "retrieve", "post": "create"}), name="audio_data"),
    path("video/", VideoDataViewSet.as_view({"get": "retrieve", "post": "create"}), name="video_data"),
]
