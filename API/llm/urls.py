from django.urls import include, path
from rest_framework.routers import DefaultRouter

from llm.views import CallLLMView, APILLMCall

router = DefaultRouter()
router.register(r'call-llm', CallLLMView, basename='call-llm')

urlpatterns = [
    path("", include(router.urls)),

    path("api/", APILLMCall.as_view(), name="api-llm-call"),
]
