import logging

from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from authenticate.serializers import (
    APIReturnTokenSerializer,
    APITokenObtainPairSerializer,
    UpdatePasswordSerializer,
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


class ObtainAuthTokenView(APIView):
    permission_classes = (
        permissions.IsAuthenticated,
    )  # Specify any permission classes if needed

    def post(self, request):
        try:
            # check whether token exists for the user
            token_exists = Token.objects.filter(user=request.user).exists()
            if token_exists:
                # delete it and create a new one

                token = Token.objects.get(user=request.user)
                token.delete()
                token = Token.objects.create(user=request.user)

                return Response({"token": token.key}, status=status.HTTP_200_OK)
            token, created = Token.objects.get_or_create(user=request.user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error obtaining token: {e}")
            return Response({"error": "Error obtaining token"}, status=400)


class UpdatePasswordView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        serializer = UpdatePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data["old_password"]):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Set the new password
            user.set_password(serializer.validated_data["new_password"])
            user.save()
            return Response(
                {"success": "Password updated successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
