from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authenticate.utils.get_logger import get_logger
from llm.models import LLMRequestRecord
from orchestrator.models import Task, TaskWorker
from orchestrator.serializers import (
    TaskCustomLLMRequestSerializer,
    TaskLLMRequestSerializer,
    TaskLLMRequestsSerializer,
    TaskReportSerializer,
    TaskSerializer,
    TaskSTTRequestSerializer,
    TaskWorkerSerializer,
)

logger = get_logger(__name__)


class QueueTaskViewSet(viewsets.ViewSet):
    """
    A ViewSet for queuing LLM and STT tasks.
    """

    # This ensures that only authenticated users can access these endpoints
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="LLM Single Task Queue",
        operation_description="Queue Large Language Model (LLM) tasks with a prompt",
        request_body=TaskLLMRequestSerializer,
        responses={200: "Task queued successfully"},
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def llm(self, request):
        """
        Endpoint to queue Large Language Model (LLM) tasks.
        """
        data = request.data
        serializer = TaskLLMRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        task_id = self.__queue_task(
            user=request.user,
            task_type=serializer.validated_data["task_type"],
            name=serializer.data["name"],
            data=serializer.data,
        )
        return Response(
            {"message": "LLM task queued successfully", "task_id": task_id},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="LLM Batch Tasks Queue",
        operation_description="Queue a list of prompts for Large Language Model (LLM) tasks",
        request_body=TaskLLMRequestsSerializer,
        responses={200: "Tasks queued successfully"},
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def llm_batch(self, request):
        """
        Endpoint to queue a list of prompts for Large Language Model (LLM) tasks.
        """
        # Example task queuing logic
        serializer = TaskLLMRequestsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        task_ids = [
            self.__queue_task(
                user=request.user,
                task_type=serializer.validated_data["task_type"],
                name=serializer.data["name"],
                data={
                    "model_name": request.data["model_name"],
                    "prompt": prompt,
                    "llm_task_type": request.data.get(
                        "llm_task_type", "chat_completion"
                    ),
                },
            )
            for prompt in data["prompts"]
        ]
        return Response(
            {"message": "LLM tasks queued successfully", "task_ids": task_ids},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="LLM Custom Task Queue",
        operation_description="""Custom Queue Large Language Model (LLM) tasks, 
                              with more flexibility to customize the parameters of the task
                              """,
        request_body=TaskCustomLLMRequestSerializer,
        responses={200: "Task queued successfully"},
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def custom_llm(self, request):
        """
        Endpoint to queue Large Language Model (LLM) tasks.
        """
        data = request.data
        serializer = TaskCustomLLMRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        task_id = self.__queue_task(
            user=request.user,
            task_type=serializer.validated_data["task_type"],
            name=serializer.validated_data["name"],
            data=serializer.data,
        )
        return Response(
            {"message": "LLM task queued successfully", "task_id": task_id},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="STT Task Queue",
        operation_description="Queue Speech To Text (STT) tasks",
        request_body=TaskSTTRequestSerializer,
        responses={200: "Task queued successfully"},
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def stt(self, request):
        """
        Endpoint to queue Speech To Text (STT) tasks.
        """
        # Example task queuing logic
        serializer = TaskSTTRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_id = self.__queue_task(
            user=request.user, task_type="stt", name="stt", data=serializer.data
        )
        return Response(
            {"message": "STT task queued successfully", "task_id": task_id},
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def __queue_task(user, task_type: str, name: str, data: dict):
        """
        Simulates task queuing logic. Replace with actual implementation.
        """
        logger.info(f"Queueing {task_type} task with data: {data}")
        # Simulate task queuing and return a mock task ID

        task = Task.create_task(
            user=user,
            name=name,
            work_type=task_type,
            parameters=data,
        )
        logger.info(f"Task {task.id} queued successfully")
        return task.id

    # add an endpoint to get the task for GPU
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
    def task(self, request, task_name="gpu"):
        """
        Endpoint to get the task for GPU.
        """
        logger.info(f"Getting task for GPU")
        try:
            task = Task.objects.filter(
                work_type=task_name, result_status="pending"
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

        serializer = TaskReportSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        task = Task.objects.filter(id=pk).first()
        if task is None:
            return Response(
                {"error": f"Task with ID {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        task.result_status = data.get("result_status", task.result_status)
        task.description = data.get("description", task.description)
        task.save()
        try:
            # at the same time, create a LLMRequestRecord
            prompt = task.parameters.get("prompt", None)
            if prompt is None:
                messages = task.parameters.get("messages", None)
                functions = task.parameters.get("functions", None)
                function_call = task.parameters.get("function_call", None)
                prompt = f"messages: {str(messages)}, functions: {str(functions)}, function_call: {str(function_call)}"
            llm_record = LLMRequestRecord(
                user=task.user,
                name=task.name,
                model_name=task.parameters.get("model_name"),
                prompt=prompt,
                task=task.parameters.get("llm_task_type"),
                completed_in_seconds=data.get("completed_in_seconds", 0),
                success=data.get("success", True),
                response=data.get("result", {}),
            )
            llm_record.save()
        except Exception as e:
            logger.error(f"Error saving LLMRequestRecord: {e}")
            logger.exception(e)
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
        serializer = TaskReportSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        uuid = data.get("uuid")
        mac_address = data.get("mac_address")
        ip_address = data.get("ip_address")
        task_type = data.get("task_type")

        gpu_worker, created = TaskWorker.objects.get_or_create(
            uuid=uuid,
            defaults={
                "mac_address": mac_address,
                "ip_address": ip_address,
                "task_type": task_type,
            },
        )
        if not created:
            gpu_worker.mac_address = mac_address
            gpu_worker.ip_address = ip_address
            gpu_worker.save()

        return Response(
            {"message": f"Worker {uuid} registered or updated successfully"},
            status=status.HTTP_200_OK,
        )

    # add an endpoint to check the status of a task
    @swagger_auto_schema(
        operation_summary="User: Task Status Check",
        operation_description="Check the status of a task",
        responses={200: "Task status retrieved successfully"},
    )
    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="status",
        url_name="status",
    )
    def status(self, request, pk=None):
        """
        Endpoint to check the status of a task.
        """

        logger.info(f"Checking status of task with ID: {pk}")
        try:
            task = Task.objects.filter(id=pk, user=request.user).first()
            if task is None:
                return Response(
                    {"error": f"Task with ID {pk} does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            return Response(
                {"status": task.result_status, "desc": task.description},
                status=status.HTTP_200_OK,
            )
        except Task.DoesNotExist:
            return Response(
                {"error": f"Task with ID {pk} does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )
