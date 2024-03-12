from django.urls import path, include
from rest_framework.routers import DefaultRouter
from worker.views import QueueTaskViewSet

router = DefaultRouter()
router.register(r'', QueueTaskViewSet, basename='')

urlpatterns = [
    path('', include(router.urls)),
]
