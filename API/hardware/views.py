import logging
from datetime import datetime

import pytz
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema

# Create your views here.
from rest_framework import status, viewsets
from rest_framework.decorators import action
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

    @swagger_auto_schema(
        operation_summary="Get an audio data s3 url",
        operation_description="Get an audio data",
        responses={200: "The audio data"},
        tags=["hardware"],
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="get_audio_data",
        url_name="get_audio_data",
    )
    def get_audio_data(self, request):
        """Override the post method to add custom swagger documentation."""
        audio_id = request.data.get("audio_id", None)
        if audio_id is None:
            return Response(
                {"message": "audio_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        audio_obj = DataAudio.objects.filter(id=audio_id).first()
        if audio_obj is None:
            return Response(
                {"message": "No audio data found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        s3_client = settings.BOTO3_SESSION.client("s3")
        try:
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.CSV_BUCKET,
                    "Key": f"Listener/audio/{audio_obj.uid}/audio/{audio_obj.audio_file}",
                },
                ExpiresIn=3600,
            )

            return Response({"audio_url": response}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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

    @swagger_auto_schema(
        operation_summary="Get a video data s3 url",
        operation_description="Get a video data",
        responses={200: "The video data"},
        tags=["hardware"],
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="get_video_data",
        url_name="get_video_data",
    )
    def get_video_data(self, request):
        video_id = request.data.get("video_id", None)
        if video_id is None:
            return Response(
                {"message": "video_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        video_obj = DataVideo.objects.filter(id=video_id).first()
        if video_obj is None:
            return Response(
                {"message": "No video data found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        s3_client = settings.BOTO3_SESSION.client("s3")
        try:
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.CSV_BUCKET,
                    "Key": f"Listener/videos/{video_obj.uid}/{video_obj.video_file}",
                },
                ExpiresIn=3600,
            )

            return Response({"video_url": response}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
        if (home_id is not None) and (home_id != "None"):
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

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset is None:
            return Response(
                {"message": "No text to speech found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        item = queryset[0]

        s3_url = None
        if item.text2speech_file is not None:
            try:
                s3_client = settings.BOTO3_SESSION.client("s3")
                response = s3_client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": settings.CSV_BUCKET,
                        "Key": f"tts/{item.text2speech_file}",
                    },
                    ExpiresIn=3600,
                )
                s3_url = response

            except Exception as e:
                logger.error(e)
        data = Text2SpeechSerializer(item).data
        data["tts_url"] = s3_url
        logger.info(s3_url)
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Get speech audio s3 url",
        operation_description="Get the text to speech audio s3 url",
        responses={200: "The text to speech"},
        tags=["hardware"],
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="get_text_to_speech",
        url_name="get_text_to_speech",
    )
    def get_text_to_speech(self, request):
        """Override the post method to add custom swagger documentation."""
        text2speech_id = request.data.get("text2speech_id", None)
        if text2speech_id is None:
            return Response(
                {"message": "text2speech_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        text2speech_obj = Text2Speech.objects.filter(id=text2speech_id).first()
        if text2speech_obj is None:
            return Response(
                {"message": "No text to speech found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        s3_client = settings.BOTO3_SESSION.client("s3")
        try:
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.CSV_BUCKET,
                    "Key": f"tts/{text2speech_obj.text2speech_file}",
                },
                ExpiresIn=3600,
            )

            return Response({"tts_url": response}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
