import logging
from datetime import datetime

import pytz

# Create your views here.
from rest_framework import status, viewsets
from rest_framework.response import Response

from hardware.models import AudioData, HardWareDevice, Text2Speech, VideoData
from hardware.serializers import (
    AudioDataSerializer,
    HardWareDeviceSerializer,
    Text2SpeechSerializer,
    VideoDataSerializer,
)

logger = logging.getLogger(__name__)


class HardWareDeviceViewSet(viewsets.ModelViewSet):
    queryset = HardWareDevice.objects.all()
    serializer_class = HardWareDeviceSerializer


class AudioDataViewSet(viewsets.ModelViewSet):
    queryset = AudioData.objects.all()
    serializer_class = AudioDataSerializer


class VideoDataViewSet(viewsets.ModelViewSet):
    queryset = VideoData.objects.all()
    serializer_class = VideoDataSerializer

    # overwrite the create method
    def create(self, request, *args, **kwargs):
        serializer = VideoDataSerializer(data=request.data)
        if serializer.is_valid():
            logger.critical(serializer.data)
            data = serializer.data

            video_record_minute = data["video_file"].split("/")[-1].split(".")[0]

            video_record_minute = datetime.strptime(
                video_record_minute, "%Y-%m-%d_%H-%M-%S"
            )
            # get it to be timezone aware
            # Specify the timezone: Australia/Perth
            perth_timezone = pytz.timezone("Australia/Perth")
            # Make the datetime object timezone-aware
            video_record_minute_aware = perth_timezone.localize(video_record_minute)

            # only get it to the minute level, and ignore the second level
            video_record_minute = video_record_minute_aware.replace(second=0)
            # get it timezone aware

            data["video_record_minute"] = video_record_minute
            serializer = VideoDataSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Text2SpeechViewSet(viewsets.ModelViewSet):
    queryset = Text2Speech.objects.all()
    serializer_class = Text2SpeechSerializer

    # retrieve it based on the mac address
    def get_queryset(self):
        queryset = Text2Speech.objects.all()
        mac_address = self.request.query_params.get("mac_address", None)
        if mac_address is not None:
            # order by created_at, the oldest one will be the first one
            queryset = queryset.filter(
                hardware_device_mac_address=mac_address, spoken=False
            )

        queryset = queryset.order_by("created_at")
        item = queryset.first()
        if item:
            item.spoken = True
            item.save()
        if item:
            return [item]
        else:
            return None
