import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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


class Jarv5TokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh = RefreshToken(request.data.get("refresh"))

            # Verify the token is valid and can be refreshed
            data = {"access": str(refresh.access_token)}

            refresh.set_jti()
            refresh.set_exp()

            data["refresh"] = str(refresh)

            return Response(data)
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return Response({"error": "Error refreshing token"}, status=400)
