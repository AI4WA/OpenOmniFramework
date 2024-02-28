from django.urls import path, include
from llm.views import CallLLMView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'call-llm', CallLLMView, basename='call-llm')

urlpatterns = [
    path("", include(router.urls)),
]
