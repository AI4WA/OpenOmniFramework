import logging

from django.contrib.auth.models import update_last_login
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView

from authenticate.models import User
from authenticate.serializers import (
    APIReturnTokenSerializer,
    APITokenObtainPairSerializer,
)

logger = logging.getLogger(__name__)


class APITokenObtainPairView(TokenObtainPairView):
    serializer_class = APITokenObtainPairSerializer

    @swagger_auto_schema(
        operation_description="Obtain JSON Web Token pair for user",
        responses={200: APIReturnTokenSerializer},
    )
    def post(self, request, *args, **kwargs):
        """Override the post method to add custom swagger documentation."""
        return super().post(request, *args, **kwargs)
