from django.urls import path

from authenticate.views import (
    APITokenObtainPairView,
    Jarv5TokenRefreshView,
    ObtainAuthTokenView,
    UpdatePasswordView,
)

urlpatterns = [
    path("api/token/", APITokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Keep the refresh token view unchanged
    path("api/token/refresh/", Jarv5TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/obtain/", ObtainAuthTokenView.as_view(), name="token_obtain"),
    path("api/update_password/", UpdatePasswordView.as_view(), name="update_password"),
]
