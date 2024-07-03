import logging

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from llm.models import LLMConfigRecords, LLMRequestResultDownload
from llm.serializers import (
    LLMConfigRecordsSerializer,
    LLMRequestResultDownloadSerializer,
)
from orchestrator.models import Task

logger = logging.getLogger(__name__)


class LLMConfigViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LLMConfigRecordsSerializer
    """
    List all available llm config records
    """
    queryset = LLMConfigRecords.objects.all()

    @swagger_auto_schema(
        operation_summary="List LLM Model",
        operation_description="Obtain the list of available LLM models and their status, need to have a token",
        responses={200: LLMConfigRecordsSerializer(many=True)},
        tags=["llm"],
    )
    @csrf_exempt
    def list(self, request, *args, **kwargs):
        """Override the post method to add custom swagger documentation."""
        return super().list(request, *args, **kwargs)


class LLMTaskDownloadViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Request to download LLM Task Result",
        operation_description="Download the result of the LLM task, need to have a token to access",
        request_body=LLMRequestResultDownloadSerializer,
        responses={200: "The task result"},
        tags=["llm"],
    )
    def post(self, request):
        """Override the post method to add custom swagger documentation."""
        serializer = LLMRequestResultDownloadSerializer(data=request.data)

        if serializer.is_valid():
            task_name = serializer.data.get("task_name")
            logger.info(f"Downloading the result of the task: {task_name}")
            # create a task to download the result
            download_task = LLMRequestResultDownload(name=task_name, user=request.user)
            download_task.save()

            Task.create_task(
                user=request.user,
                name=f"Download {task_name}",
                work_type="cmc",
                parameters={
                    "command": "export_to_csv",
                    "options": {
                        "task_name": task_name,
                        "task_id": download_task.id,
                        "user_id": request.user.id,
                    },
                },
            )
            return Response(
                {"message": "Task created successfully."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Download an output CSV Result",
        operation_description="Download the result of the LLM task, need to have a token to access",
        responses={200: "The task result"},
        tags=["llm"],
    )
    # task_id will be in the url
    @action(
        detail=False,
        methods=["get"],
        url_path="download/<int:task_id>",
        url_name="download_csv",
        permission_classes=[IsAuthenticated],
    )
    def download(self, request, task_id):
        """Override the post method to add custom swagger documentation."""
        task = LLMRequestResultDownload.objects.filter(
            id=task_id, user=request.user
        ).first()
        if task is None:
            return Response(
                {"message": "Task not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if task.download_link is None:
            return Response(
                {"message": "Task not ready for download."},
                status=status.HTTP_404_NOT_FOUND,
            )
        # download the file from s3
        s3 = settings.BOTO3_SESSION.client("s3")
        response = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.CSV_BUCKET, "Key": task.download_link},
            ExpiresIn=3600,
        )
        return Response({"download_link": response}, status=status.HTTP_200_OK)
