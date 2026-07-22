from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .views import UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = [
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/logout/", TokenBlacklistView.as_view(), name="logout"),
    path("", include(router.urls)),
]
