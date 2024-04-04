from django.urls import path

from llm.views import LLMConfigViewSet

urlpatterns = [
    path("config", LLMConfigViewSet.as_view({"get": "list"}), name="config"),
]
