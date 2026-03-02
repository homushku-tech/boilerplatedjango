from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
urlpatterns = [
    path('admin/', admin.site.urls),
    # jwt tokens
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
]
