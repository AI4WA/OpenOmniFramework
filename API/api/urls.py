"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

admin.site.site_header = "UWA NLP TLP"
admin.site.site_title = "WA Data & LLM Platform Admin Portal"
admin.site.index_title = "UWA NLP TLP"

schema_view = get_schema_view(
    openapi.Info(
        title="WA Data & LLM Platform API Documentation",
        default_version="v1",
        description="API description for you to queue LLM tasks, authenticate, and interact with hardware.",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("authenticate/", include("authenticate.urls")),
    path("hardware/", include("hardware.urls")),
    path("queue_task/", include("orchestrator.urls")),
    path("llm/", include("llm.urls")),
    path(
        "swagger/",
        login_required(schema_view.with_ui("swagger", cache_timeout=0)),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="redoc"),
    path("", admin.site.urls),
]
