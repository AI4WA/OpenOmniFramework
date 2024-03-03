from django.urls import include, path
from rest_framework.routers import DefaultRouter

from llm.views import CallLLMView

router = DefaultRouter()
router.register(r'call-llm', CallLLMView, basename='call-llm')

urlpatterns = [
    path("", include(router.urls)),
]
