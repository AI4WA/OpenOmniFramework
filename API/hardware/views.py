from django.shortcuts import render
# Create your views here.
from rest_framework import viewsets

from hardware.models import AudioData, VideoData, HardWareDevice, Text2Speech
from hardware.serializers import AudioDataSerializer, VideoDataSerializer, HardWareDeviceSerializer, \
    Text2SpeechSerializer


class HardWareDeviceViewSet(viewsets.ModelViewSet):
    queryset = HardWareDevice.objects.all()
    serializer_class = HardWareDeviceSerializer


class AudioDataViewSet(viewsets.ModelViewSet):
    queryset = AudioData.objects.all()
    serializer_class = AudioDataSerializer


class VideoDataViewSet(viewsets.ModelViewSet):
    queryset = VideoData.objects.all()
    serializer_class = VideoDataSerializer


class Text2SpeechViewSet(viewsets.ModelViewSet):
    queryset = Text2Speech.objects.all()
    serializer_class = Text2SpeechSerializer

    # retrieve it based on the mac address
    def get_queryset(self):
        queryset = Text2Speech.objects.all()
        mac_address = self.request.query_params.get('mac_address', None)
        if mac_address is not None:
            # order by created_at, the oldest one will be the first one
            queryset = queryset.filter(hardware_device_mac_address=mac_address, spoken=False)

        queryset = queryset.order_by('created_at')
        item = queryset.first()
        if item:
            item.spoken = True
            item.save()
        if item:
            return [item]
        else:
            return None
