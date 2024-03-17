import logging
import time

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from worker.models import Task
from worker.serializers import (TaskLLMRequestSerializer,
                                TaskLLMRequestsSerializer,
                                TaskSTTRequestSerializer)

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
        responses={200: 'Task queued successfully'}
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def llm(self, request):
        """
        Endpoint to queue Large Language Model (LLM) tasks.
        """
        data = request.data
        serializer = TaskLLMRequestSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        task_id = self.__queue_task(user=request.user,
                                    task_type='llm',
                                    data=serializer.data)
        return Response({'message': 'LLM task queued successfully', 'task_id': task_id}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Queue a list of prompts for Large Language Model (LLM) tasks",
        request_body=TaskLLMRequestsSerializer,
        responses={200: 'Tasks queued successfully'}
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def llm_batch(self, request):
        """
        Endpoint to queue a list of prompts for Large Language Model (LLM) tasks.
        """
        # Example task queuing logic
        serializer = TaskLLMRequestsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        task_ids = [self.__queue_task(user=request.user,
                                      task_type='llm',
                                      data={'model_name': request.data['model_name'], 'prompt': prompt})
                    for prompt in data['prompts']]
        return Response({'message': 'LLM tasks queued successfully', 'task_ids': task_ids}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Queue Speech To Text (STT) tasks",
        request_body=TaskSTTRequestSerializer,
        responses={200: 'Task queued successfully'}
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def stt(self, request):
        """
        Endpoint to queue Speech To Text (STT) tasks.
        """
        # Example task queuing logic
        serializer = TaskSTTRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task_id = self.__queue_task(
            user=request.user,
            task_type='stt',
            data=serializer.data)
        return Response({'message': 'STT task queued successfully', 'task_id': task_id}, status=status.HTTP_200_OK)

    @staticmethod
    def __queue_task(user, task_type, data):
        """
        Simulates task queuing logic. Replace with actual implementation.
        """
        logger.info(f"Queueing {task_type} task with data: {data}")
        # Simulate task queuing and return a mock task ID

        task = Task.create_task(user=user,
                                name=f"{task_type}_{time.time()}",
                                work_type=task_type,
                                parameters=data)
        logger.info(f"Task {task.id} queued successfully")
        return task.id

    # add an endpoint to check the status of a task
    @swagger_auto_schema(
        operation_description="Check the status of a task",
        responses={200: 'Task status retrieved successfully'}
    )
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='status', url_name='status')
    def status(self, request, pk=None):
        """
        Endpoint to check the status of a task.
        """

        logger.info(f"Checking status of task with ID: {pk}")
        try:
            task = Task.objects.filter(id=pk, user=request.user).first()
            if task is None:
                return Response({'error': f'Task with ID {pk} does not exist'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'status': task.result_status, "desc": task.description}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({'error': f'Task with ID {pk} does not exist'}, status=status.HTTP_404_NOT_FOUND)
