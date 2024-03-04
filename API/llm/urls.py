from django.urls import include, path
from rest_framework.routers import DefaultRouter

from llm.views import CallLLMView, LLMConfigViewSet

router = DefaultRouter()
router.register(r'call-llm', CallLLMView, basename='call-llm')

urlpatterns = [
    path("", include(router.urls)),
    path("config", LLMConfigViewSet.as_view({'get': 'list'}), name="config"),
]
