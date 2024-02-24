from django.urls import path
from hardware.views import AudioDataViewSet

urlpatterns = [
    path("audio/", AudioDataViewSet.as_view({"get": "retrieve", "post": "create"}), name="audio_data"),
]
