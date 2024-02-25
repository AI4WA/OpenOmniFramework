from django.shortcuts import render
from llm.llm_call.llm_adaptor import LLMAdaptor
from llm.serializers import LLMRequestSerializer
from drf_yasg.utils import swagger_auto_schema
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class CallLLMView(APIView):

    @swagger_auto_schema(request_body=LLMRequestSerializer)
    def post(self, request):
        serializer = LLMRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        model_name = serializer.validated_data["model_name"]
        prompt = serializer.validated_data["prompt"]

        adaptor = LLMAdaptor(model_name)
        response = adaptor.get_response(prompt)
        logger.info(response)
        return Response(response, status=status.HTTP_200_OK)
