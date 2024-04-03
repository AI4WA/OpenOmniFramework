import logging
import time

from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from llm.llm_call.llm_adaptor import LLMAdaptor
from llm.models import LLMConfigRecords, LLMRequestRecord
from llm.serializers import (
    LLMConfigRecordsSerializer,
    LLMCustomRequestSerializer,
    LLMRequestSerializer,
    LLMResponseSerializer,
)

logger = logging.getLogger(__name__)


class CallLLMView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Call the LLM model to do the chat completion, not all models support this feature",
        request_body=LLMRequestSerializer,
        responses={200: LLMResponseSerializer},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="chat-completion",
        url_name="chat-completion",
    )
    @csrf_exempt
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
                completed_in_seconds=end_time - start_time,
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
                completed_in_seconds=end_time - start_time,
            )
            record.save()
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        operation_description="Call the LLM model to do the custom chat completion in a json format, "
        "not all models support this feature for models without embedding features, it will "
        "throw an error",
        request_body=LLMCustomRequestSerializer,
        responses={200: LLMResponseSerializer},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="custom-chat-completion",
        url_name="custom-chat-completion",
    )
    @csrf_exempt
    def custom_chat_completion(self, request):
        """
        Call the LLM model to do the custom chat completion
        """

        serializer = LLMCustomRequestSerializer(data=request.data)
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
                prompt=str(prompt),
                response=response,
                task="chat-completion",
                completed_in_seconds=end_time - start_time,
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
                prompt=str(prompt),
                response=str(e),
                success=False,
                task="chat-completion",
                completed_in_seconds=end_time - start_time,
            )
            record.save()
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # add another url: post to create embedding

    @swagger_auto_schema(
        request_body=LLMRequestSerializer,
        operation_description="Call the LLM model to create embeddings,"
        "not all models support this feature, "
        "for models without embedding features, it will throw an error",
        responses={200: LLMResponseSerializer},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-embedding",
        url_name="create-embedding",
    )
    @csrf_exempt
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
                task="create_embedding",
                completed_in_seconds=end_time - start_time,
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
                task="create_embedding",
                completed_in_seconds=end_time - start_time,
            )
            record.save()
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @swagger_auto_schema(
        request_body=LLMRequestSerializer,
        responses={200: LLMResponseSerializer},
        operation_description="Call the LLM model to complete the prompt",
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="completion",
        url_name="completion",
    )
    @csrf_exempt
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
                completed_in_seconds=end_time - start_time,
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
                completed_in_seconds=end_time - start_time,
            )
            record.save()
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LLMConfigViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LLMConfigRecordsSerializer
    """
    List all available llm config records
    """
    queryset = LLMConfigRecords.objects.all()

    @swagger_auto_schema(
        operation_description="Obtain the list of available LLM models and their status, need to have a token to access",
        responses={200: LLMConfigRecordsSerializer(many=True)},
        tags=["llm"],
    )
    @csrf_exempt
    def list(self, request, *args, **kwargs):
        """Override the post method to add custom swagger documentation."""
        return super().list(request, *args, **kwargs)
