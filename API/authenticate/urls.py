from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from authenticate.views import APITokenObtainPairView

urlpatterns = [
    path('api/token/', APITokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Keep the refresh token view unchanged
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
