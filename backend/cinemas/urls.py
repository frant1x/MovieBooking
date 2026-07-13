from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CinemaViewSet

router = DefaultRouter()
router.register(r"", CinemaViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
