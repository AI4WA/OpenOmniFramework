from django.urls import include, path
from rest_framework.routers import DefaultRouter

from chat.views import ChatViewSet

router = DefaultRouter()
router.register(r"", ChatViewSet, basename="")

urlpatterns = [
    path("", include(router.urls)),
]
