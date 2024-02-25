from django.urls import path
from authenticate.views import MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Keep the refresh token view unchanged
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
