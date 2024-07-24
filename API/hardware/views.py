import logging

# Create your views here.
from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from moviepy.editor import VideoFileClip, concatenate_videoclips
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from hardware.models import (
    DataAudio,
    DataMultiModalConversation,
    DataVideo,
    HardWareDevice,
    Home,
    ResSpeech,
)
from hardware.serializers import (
    AudioDataSerializer,
    HardWareDeviceSerializer,
    ResSpeechSerializer,
    VideoDataSerializer,
)

logger = logging.getLogger(__name__)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def storage_solution(request):
    return Response(
        {"storage_solution": settings.STORAGE_SOLUTION}, status=status.HTTP_200_OK
    )


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
                    "Bucket": settings.S3_BUCKET,
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
                    "Bucket": settings.S3_BUCKET,
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
    queryset = ResSpeech.objects.all()
    serializer_class = ResSpeechSerializer

    # retrieve it based on the mac address
    def get_queryset(self):
        queryset = ResSpeech.objects.filter(
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
                        "Bucket": settings.S3_BUCKET,
                        "Key": f"tts/{item.text2speech_file}",
                    },
                    ExpiresIn=3600,
                )
                s3_url = response

            except Exception as e:
                logger.error(e)
        data = ResSpeechSerializer(item).data
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
        text2speech_obj = ResSpeech.objects.filter(id=text2speech_id).first()
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
                    "Bucket": settings.S3_BUCKET,
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


# return audio data from local storage
def client_audio(request, audio_id):
    audio_obj = DataAudio.objects.filter(id=audio_id).first()
    if audio_obj is None:
        return HttpResponse(
            "No audio data found.",
            content_type="text/plain",
        )

    if (settings.STORAGE_SOLUTION == settings.STORAGE_SOLUTION_S3) or (
        settings.STORAGE_SOLUTION == settings.STORAGE_SOLUTION_API
    ):

        # we will grab it from the s3 and return it
        s3_client = settings.BOTO3_SESSION.client("s3")
        # construct the key and then create the pre-signed url
        s3_key = f"Listener/audio/{audio_obj.uid}/{audio_obj.audio_file}"
        local_file = (
            settings.CLIENT_MEDIA_ROOT / "audio" / audio_obj.uid / audio_obj.audio_file
        )
        # check if the file exists locally
        if not local_file.exists():
            local_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                s3_client.download_file(
                    settings.S3_BUCKET,
                    s3_key,
                    local_file,
                )
            except Exception as e:
                logger.error(e)
                # response with the HttpResponse
                response = HttpResponse(
                    str(e),
                    content_type="text/plain",
                )
                return response

    audio_file = (
        settings.CLIENT_MEDIA_ROOT / "audio" / audio_obj.uid / audio_obj.audio_file
    )
    with open(audio_file, "rb") as f:
        response = HttpResponse(f.read(), content_type="audio/mpeg")
        response["Content-Disposition"] = f"attachment; filename={audio_obj.audio_file}"
    return response


def ai_audio(request, audio_id):
    logger.info(f"Audio id: {audio_id}")
    res_audio_obj = ResSpeech.objects.filter(id=audio_id).first()
    if res_audio_obj is None:
        return HttpResponse("No audio data found.", content_type="text/plain")

    if (settings.STORAGE_SOLUTION == settings.STORAGE_SOLUTION_S3) or (
        settings.STORAGE_SOLUTION == settings.STORAGE_SOLUTION_API
    ):
        # we will grab it from the s3 and return it
        s3_client = settings.BOTO3_SESSION.client("s3")
        s3_key = f"Responder/tts/{res_audio_obj.text2speech_file.split('/')[-1]}"
        local_file = (
            settings.AI_MEDIA_ROOT / res_audio_obj.text2speech_file.split("/")[-1]
        )
        # check if the file exists locally
        if not local_file.exists():
            local_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                s3_client.download_file(
                    settings.S3_BUCKET,
                    s3_key,
                    local_file,
                )
            except Exception as e:
                logger.error(e)
                # response with the HttpResponse
                response = HttpResponse(
                    str(e),
                    content_type="text/plain",
                )
                return response

    audio_file = settings.AI_MEDIA_ROOT / res_audio_obj.text2speech_file.split("/")[-1]
    logger.info(audio_file)
    with open(audio_file, "rb") as f:
        response = HttpResponse(f.read(), content_type="audio/mpeg")
        response["Content-Disposition"] = (
            f"attachment; filename={res_audio_obj.text2speech_file}"
        )
    return response


def combine_videos(video1_paths, output_path):
    clips = []
    for video1_path in video1_paths:
        clip = VideoFileClip(video1_path)
        clips.append(clip)
    final_clip = concatenate_videoclips([clip for clip in clips])
    final_clip.write_videofile(output_path, codec="libx264")


def client_video(request, conversation_id):
    conversation = DataMultiModalConversation.objects.filter(id=conversation_id).first()
    if conversation is None:
        return Response(
            {"message": "No video data found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    videos = conversation.video.all().order_by("start_time")
    if len(videos) == 0:
        return Response(
            {"message": "No video data found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    video_paths = []
    for video in videos:
        video_path = (
            settings.CLIENT_MEDIA_ROOT / "videos" / video.uid / video.video_file
        )
        if not video_path.exists() and (
            settings.STORAGE_SOLUTION == settings.STORAGE_SOLUTION_S3
            or settings.STORAGE_SOLUTION == settings.STORAGE_SOLUTION_API
        ):
            video_path.parent.mkdir(parents=True, exist_ok=True)
            s3_client = settings.BOTO3_SESSION.client("s3")
            s3_key = f"Listener/videos/{video.uid}/{video.video_file}"
            try:
                s3_client.download_file(
                    settings.S3_BUCKET,
                    s3_key,
                    video_path,
                )
            except Exception as e:
                logger.error(e)
                # response with the HttpResponse
                response = HttpResponse(
                    str(e),
                    content_type="text/plain",
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
                return
        video_paths.append(video_path.as_posix())

    output_path = (
        settings.CLIENT_MEDIA_ROOT / "conversations" / f"{conversation.id}.mp4"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not output_path.exists():
        output_path = output_path.as_posix()

        combine_videos(video_paths, output_path)
    with open(output_path, "rb") as f:
        response = HttpResponse(f.read(), content_type="video/mp4")
        response["Content-Disposition"] = f"attachment; filename={conversation.id}.mp4"
    return response


# create an endpoint as relay to upload files to S3
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_file(request):
    """
    This is for temporarily solution, as we host the centre server,
    and will not provide the S3 access to the general user

    So to testout our system, you can use this endpoint to upload files to S3
    Focus on client and AI side

    """
    file = request.FILES.get("file")
    if file is None:
        return Response(
            {"message": "No file found."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    s3_client = settings.BOTO3_SESSION.client("s3")
    dest_path = request.data.get("dest_path", None)
    if dest_path is None:
        return Response(
            {"message": "dest_path is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        s3_client.upload_fileobj(
            file,
            settings.S3_BUCKET,
            dest_path,
        )
        return Response(
            {"message": "File uploaded successfully."},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(e)
        return Response(
            {"message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_files(request):
    """
    List all the files in the S3 bucket
    """
    from_time = request.data.get("from_time", None)
    logger.info(f"From time: {from_time}")
    if from_time is None:
        # default to 100 day ago
        from_time = datetime.now() - timedelta(days=100)
    else:
        # get the from_time from the timestamp
        from_time = datetime.fromtimestamp(float(from_time))

    audio_files = DataAudio.objects.filter(created_at__gte=from_time)
    video_files = DataVideo.objects.filter(created_at__gte=from_time)
    audio_list_json = AudioDataSerializer(audio_files, many=True).data
    video_list_json = VideoDataSerializer(video_files, many=True).data
    return Response(
        {"audio_files": audio_list_json, "video_files": video_list_json},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def download_file_link(request):
    file_type = request.data.get("file_type", None)
    file_id = request.data.get("file_id", None)
    if file_type not in ["audio", "video"]:
        return Response(
            {"message": "Invalid file type."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if file_id is None:
        return Response(
            {"message": "file_id is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if file_type == "audio":
        audio_obj = DataAudio.objects.filter(id=file_id).first()
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
                    "Bucket": settings.S3_BUCKET,
                    "Key": f"Listener/audio/{audio_obj.uid}/{audio_obj.audio_file}",
                },
                ExpiresIn=3600,
            )

            return Response({"audio_url": response}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:
        video_obj = DataVideo.objects.filter(id=file_id).first()
        if video_obj is None:
            return Response(
                {"message": "No video data found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        s3_client = settings.BOTO3_SESSION.client("s3")
        try:
            video_file_url = s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": settings.S3_BUCKET,
                    "Key": f"Listener/videos/{video_obj.uid}/{video_obj.video_file}",
                },
                ExpiresIn=3600,
            )

            # all frames urls
            # then images will be within the folder /uid/frames/minute
            minute_key = video_obj.video_file.split(".")[0][:-3]
            logger.info(minute_key)
            s3_frames_prefix = f"Listener/videos/{video_obj.uid}/frames/{minute_key}"
            response = s3_client.list_objects_v2(
                Bucket=settings.S3_BUCKET,
                Prefix=s3_frames_prefix,
            )
            frames = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    frame_url = s3_client.generate_presigned_url(
                        "get_object",
                        Params={
                            "Bucket": settings.S3_BUCKET,
                            "Key": obj["Key"],
                        },
                        ExpiresIn=3600,
                    )
                    frames.append(frame_url)
            video_urls = {"video_url": video_file_url, "frames": frames}

            return Response(video_urls, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response(
                {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
