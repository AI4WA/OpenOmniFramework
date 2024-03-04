import logging
import time

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from llm.llm_call.llm_adaptor import LLMAdaptor

from llm.models import LLMRequestRecord, LLMConfigRecords
from llm.serializers import LLMRequestSerializer, LLMConfigRecordsSerializer

from rest_framework.permissions import AllowAny, IsAuthenticated

logger = logging.getLogger(__name__)


class CallLLMView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=LLMRequestSerializer)
    @action(detail=False,
            methods=['post'],
            url_path='chat-completion',
            url_name='chat-completion',
            )
    def chat_completion(self, request):
        """
        Call the LLM model to do the chat completion
        """

        serializer = LLMRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        model_name = serializer.validated_data["model_name"]
        prompt = serializer.validated_data["prompt"]

        start_time = time.time()
        try:
            adaptor = LLMAdaptor(model_name)
            response = adaptor.create_chat_completion(prompt)
            end_time = time.time()
            record = LLMRequestRecord(
                user=request.user,
                model_name=model_name,
                prompt=prompt,
                response=response,
                task="chat-completion",
                completed_in_seconds=end_time - start_time
            )
            record.save()
            logger.info(response)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            end_time = time.time()
            record = LLMRequestRecord(
                user=request.user,
                model_name=model_name,
                prompt=prompt,
                response=str(e),
                success=False,
                task="chat-completion",
                completed_in_seconds=end_time - start_time
            )
            record.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # add another url: post to create embedding

    @swagger_auto_schema(request_body=LLMRequestSerializer)
    @action(detail=False,
            methods=['post'],
            url_path='create-embedding',
            url_name='create-embedding',
            )
    def create_embedding(self, request):
        """
        Call the LLM model to create an embedding
        """
        serializer = LLMRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        model_name = serializer.validated_data["model_name"]
        prompt = serializer.validated_data["prompt"]
        start_time = time.time()
        try:
            adaptor = LLMAdaptor(model_name)
            response = adaptor.create_embedding(prompt)
            end_time = time.time()
            logger.info(response)
            record = LLMRequestRecord(
                user=request.user,
                model_name=model_name,
                prompt=prompt,
                response=response,
                task="create-embedding",
                completed_in_seconds=end_time - start_time
            )
            record.save()
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception(e)
            end_time = time.time()
            record = LLMRequestRecord(
                user=request.user,
                model_name=model_name,
                prompt=prompt,
                response=str(e),
                success=False,
                task="create-embedding",
                completed_in_seconds=end_time - start_time
            )
            record.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(request_body=LLMRequestSerializer)
    @action(detail=False,
            methods=['post'],
            url_path='completion',
            url_name='completion',
            )
    def completion(self, request):
        """
        Call the LLM model to do the completion
        """
        serializer = LLMRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        model_name = serializer.validated_data["model_name"]
        prompt = serializer.validated_data["prompt"]
        start_time = time.time()
        try:
            adaptor = LLMAdaptor(model_name)
            response = adaptor.create_completion(prompt)
            end_time = time.time()
            logger.info(response)
            record = LLMRequestRecord(
                user=request.user,
                model_name=model_name,
                prompt=prompt,
                response=response,
                task="completion",
                completed_in_seconds=end_time - start_time
            )
            record.save()
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(e)
            end_time = time.time()
            record = LLMRequestRecord(
                user=request.user,
                model_name=model_name,
                prompt=prompt,
                response=str(e),
                success=False,
                task="completion",
                completed_in_seconds=end_time - start_time
            )
            record.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LLMConfigViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LLMConfigRecordsSerializer
    """
    List all available llm config records
    """
    queryset = LLMConfigRecords.objects.all()
