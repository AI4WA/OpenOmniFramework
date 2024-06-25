from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authenticate.utils.get_logger import get_logger
from orchestrator.models import Task, TaskWorker
from orchestrator.serializers import (
    TaskReportSerializer,
    TaskRequestSerializer,
    TaskSerializer,
    TaskWorkerSerializer,
)

logger = get_logger(__name__)


class QueueTaskViewSet(viewsets.ViewSet):
    """
    A ViewSet for queuing AI tasks generally

    """

    # This ensures that only authenticated users can access these endpoints
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Queue an AI task",
        operation_description="This will include LLM, STT, and other AI tasks",
        request_body=TaskRequestSerializer,
        responses={200: "Task queued successfully"},
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def ai_task(self, request):
        """
        Endpoint to queue tasks for AI Client side to run
        """
        data = request.data
        serializer = TaskRequestSerializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Error validating task request: {e}")
            return Response(
                {"error": f"Error validating task request: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = serializer.save(user=request.user)
        task_id = task.id
        return Response(
            {"message": "LLM task queued successfully", "task_id": task_id},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="Worker: Get Task",
        operation_description="Get the task for GPU/CPU",
        responses={200: "Task retrieved successfully"},
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="task/(?P<task_name>.+)",
        url_name="task",
    )
    def task(self, request, task_name="all"):
        """
        Endpoint to get the task for AI
        """
        try:
            if task_name == "all":
                task = Task.objects.filter(result_status="pending").first()
            else:
                task = Task.objects.filter(
                    task_name=task_name, result_status="pending"
                ).first()
            if task is None:
                return Response(
                    {"error": f"No pending {task_name} tasks found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            task.result_status = "started"
            task.save()
            task_serializer = TaskSerializer(task)
            logger.critical(f"Task {task.id} retrieved successfully")
            return Response(data=task_serializer.data, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response(
                {"error": f"No pending {task_name} tasks found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    # add an endpoint to update the task result
    @swagger_auto_schema(
        operation_summary="Worker: Result Update",
        operation_description="Update the task result",
        request_body=TaskReportSerializer,
        responses={200: "Task result updated successfully"},
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="update_result",
        url_name="update_result",
    )
    def update_result(self, request, pk=None):
        """
        Endpoint to update the result of a task.
        """
        data = request.data
        task = Task.objects.filter(id=pk).first()
        if task is None:
            return Response(
                {"error": f"Task with ID {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskSerializer(data=data, instance=task, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": f"Task {task.id} updated successfully"},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="Worker: Register",
        operation_description="Register a worker",
        responses={200: "Worker registered or updated successfully"},
        request_body=TaskWorkerSerializer,
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def worker(self, request):
        """
        Endpoint to register a GPU worker.
        """
        data = request.data
        serializer = TaskWorkerSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        uuid = data.get("uuid")
        mac_address = data.get("mac_address")
        ip_address = data.get("ip_address")
        task_name = data.get("task_name")

        worker, created = TaskWorker.objects.get_or_create(
            uuid=uuid,
            defaults={
                "mac_address": mac_address,
                "ip_address": ip_address,
                "task_name": task_name,
            },
        )
        if not created:
            worker.mac_address = mac_address
            worker.ip_address = ip_address
            worker.save()

        return Response(
            {"message": f"Worker {uuid} registered or updated successfully"},
            status=status.HTTP_200_OK,
        )
