import logging

from django.contrib.auth.models import update_last_login
from rest_framework import generics, permissions, status, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenRefreshSerializer)
from rest_framework_simplejwt.views import TokenObtainPairView

from authenticate.models import User
from authenticate.serializers import APITokenObtainPairSerializer

logger = logging.getLogger(__name__)


class APITokenObtainPairView(TokenObtainPairView):
    serializer_class = APITokenObtainPairSerializer
