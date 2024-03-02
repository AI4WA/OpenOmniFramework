from django.shortcuts import render
# Create your views here.
from rest_framework import viewsets

from hardware.models import AudioData, VideoData
from hardware.serializers import AudioDataSerializer, VideoDataSerializer


class AudioDataViewSet(viewsets.ModelViewSet):
    queryset = AudioData.objects.all()
    serializer_class = AudioDataSerializer


class VideoDataViewSet(viewsets.ModelViewSet):
    queryset = VideoData.objects.all()
    serializer_class = VideoDataSerializer
