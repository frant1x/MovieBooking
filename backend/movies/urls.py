from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovieViewSet, MovieSessionViewSet

router = DefaultRouter()
router.register(r"sessions", MovieSessionViewSet, basename="moviesession")
router.register(r"", MovieViewSet, basename="movie")

urlpatterns = [
    path("", include(router.urls)),
]
