import logging
from datetime import datetime

import pytz

# Create your views here.
from rest_framework import status, viewsets
from rest_framework.response import Response

from hardware.models import DataAudio, DataVideo, HardWareDevice, Home, Text2Speech
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
    queryset = DataAudio.objects.all()
    serializer_class = AudioDataSerializer


class VideoDataViewSet(viewsets.ModelViewSet):
    queryset = DataVideo.objects.all()
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
        queryset = Text2Speech.objects.filter(
            played=False, text2speech_file__isnull=False
        )
        home_id = self.request.query_params.get("home_id", None)
        logger.info(f"Home id: {home_id}")
        if home_id is not None:
            home = Home.objects.filter(id=home_id).first()
            if not home:
                return None
            queryset = queryset.filter(
                home=home, played=False, text2speech_file__isnull=False
            )

        queryset = queryset.order_by("created_at")
        item = queryset.first()
        if item:
            item.played = True
            item.save()
        if item:
            return [item]
        else:
            return None
