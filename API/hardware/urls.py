from django.urls import path

from hardware.views import AudioDataViewSet, VideoDataViewSet, HardWareDeviceViewSet, Text2SpeechViewSet

urlpatterns = [
    path("register/", HardWareDeviceViewSet.as_view({"get": "list", "post": "create", 'put': 'update'}),
         name="hardware"),
    path("audio/", AudioDataViewSet.as_view({"get": "retrieve", "post": "create"}), name="audio_data"),
    path("video/", VideoDataViewSet.as_view({"get": "retrieve", "post": "create"}), name="video_data"),
    path("speech/", Text2SpeechViewSet.as_view({"get": "list"}), name="text2speech"),
]
