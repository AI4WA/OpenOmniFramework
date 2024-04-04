from django.urls import include, path

from llm.views import LLMConfigViewSet  # CallLLMView

# from rest_framework.routers import DefaultRouter


# as each request will take quite a while to finish, we switch to async way to handle the request
# router = DefaultRouter()
# router.register(r"call-llm", CallLLMView, basename="call-llm")

urlpatterns = [
    # path("", include(router.urls)),
    path("config", LLMConfigViewSet.as_view({"get": "list"}), name="config"),
]
