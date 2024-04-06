from django.urls import path

from llm.views import LLMConfigViewSet, LLMTaskDownloadViewSet

urlpatterns = [
    path("config", LLMConfigViewSet.as_view({"get": "list"}), name="config"),
    path("download", LLMTaskDownloadViewSet.as_view({"post": "post"}), name="download"),
    path(
        "download/<int:task_id>",
        LLMTaskDownloadViewSet.as_view({"get": "download"}),
        name="download_s3",
    ),
]
