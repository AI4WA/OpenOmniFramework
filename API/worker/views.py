import logging
import time

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from llm.models import LLMRequestRecord
from worker.models import Task
from worker.serializers import (
    TaskLLMRequestSerializer,
    TaskLLMRequestsSerializer,
    TaskReportSerializer,
    TaskSerializer,
    TaskCustomLLMRequestSerializer,
    TaskSTTRequestSerializer,
)

logger = logging.getLogger(__name__)


class QueueTaskViewSet(viewsets.ViewSet):
    """
    A ViewSet for queuing LLM and STT tasks.
    """

    # This ensures that only authenticated users can access these endpoints
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Queue Large Language Model (LLM) tasks",
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

        task_worker = serializer.validated_data["task_worker"]
        task_type = "llm" if task_worker == "cpu" else "gpu"
        task_id = self.__queue_task(
            user=request.user,
            task_type=task_type,
            name=serializer.data["name"],
            data=serializer.data,
        )
        return Response(
            {"message": "LLM task queued successfully", "task_id": task_id},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
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
        task_worker = serializer.validated_data["task_worker"]
        task_type = "llm" if task_worker == "cpu" else "gpu"
        data = serializer.validated_data
        task_ids = [
            self.__queue_task(
                user=request.user,
                task_type=task_type,
                name=serializer.data["name"],
                data={
                    "model_name": request.data["model_name"],
                    "prompt": prompt,
                    ""
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
        operation_description="Custom Queue Large Language Model (LLM) tasks",
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
        task_worker = serializer.validated_data["task_worker"]
        task_type = "llm" if task_worker == "cpu" else "gpu"
        task_id = self.__queue_task(
            user=request.user,
            task_type=task_type,
            name=serializer.data["name"],
            data=serializer.data,
        )
        return Response(
            {"message": "LLM task queued successfully", "task_id": task_id},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
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

    # add an endpoint to check the status of a task
    @swagger_auto_schema(
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

    # add an endpoint to get the task for GPU
    @swagger_auto_schema(
        operation_description="Get the task for GPU",
        responses={200: "Task retrieved successfully"},
    )
    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticated],
        url_path="gpu_task",
        url_name="gpu_task",
    )
    def gpu_task(self, request):
        """
        Endpoint to get the task for GPU.
        """
        logger.info(f"Getting task for GPU")
        try:
            task = Task.objects.filter(work_type="gpu", result_status="pending").first()
            if task is None:
                return Response(
                    {"error": f"No pending GPU tasks found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            # task.result_status = "started"
            task.save()
            task_serializer = TaskSerializer(task)
            logger.critical(f"Task {task.id} retrieved successfully")
            return Response(data=task_serializer.data, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response(
                {"error": f"No pending GPU tasks found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    # add an endpoint to update the task result
    @swagger_auto_schema(
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
        # at the same time, create a LLMRequestRecord
        llm_record = LLMRequestRecord(
            user=task.user,
            name=task.name,
            model_name=task.parameters.get("model_name"),
            prompt=task.parameters.get("prompt"),
            task=task.parameters.get("llm_task_type"),
            completed_in_seconds=data.get("completed_in_seconds", 0),
            success=data.get("success", True),
            response=data.get("result", {}),
        )
        llm_record.save()
        return Response(
            {"message": f"Task {task.id} updated successfully"},
            status=status.HTTP_200_OK,
        )
