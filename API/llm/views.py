import logging

from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from llm.models import LLMConfigRecords
from llm.serializers import LLMConfigRecordsSerializer

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
