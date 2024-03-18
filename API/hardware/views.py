from django.shortcuts import render
# Create your views here.
from rest_framework import viewsets

from hardware.models import AudioData, VideoData, HardWareDevice
from hardware.serializers import AudioDataSerializer, VideoDataSerializer, HardWareDeviceSerializer


class HardWareDeviceViewSet(viewsets.ModelViewSet):
    queryset = HardWareDevice.objects.all()
    serializer_class = HardWareDeviceSerializer


class AudioDataViewSet(viewsets.ModelViewSet):
    queryset = AudioData.objects.all()
    serializer_class = AudioDataSerializer


class VideoDataViewSet(viewsets.ModelViewSet):
    queryset = VideoData.objects.all()
    serializer_class = VideoDataSerializer
