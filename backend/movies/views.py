from rest_framework import viewsets
from .models import Movie, MovieSession
from .serializers import (
    MovieSerializer,
    CompactMovieSessionReadSerializer,
    MovieSessionReadSerializer,
    MovieSessionWriteSerializer,
)
from users.permissions import IsManagerOrAdminOrReadOnly
from datetime import date
from rest_framework.exceptions import ValidationError


class MovieViewSet(viewsets.ModelViewSet):
    """ViewSet for the Movie model."""

    serializer_class = MovieSerializer
    permission_classes = [IsManagerOrAdminOrReadOnly]

    def get_queryset(self):
        queryset = Movie.objects.all()

        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        return queryset


class MovieSessionViewSet(viewsets.ModelViewSet):
    """ViewSet for the MovieSession model."""

    permission_classes = [IsManagerOrAdminOrReadOnly]

    def get_queryset(self):
        queryset = MovieSession.objects.select_related("movie", "hall__cinema").all()

        if self.action != "list":
            return queryset

        cinema_id_param = self.request.query_params.get("cinema_id")
        if not cinema_id_param:
            raise ValidationError(
                {
                    "cinema_id": "This query parameter is required for listing movie sessions."
                }
            )
        queryset = queryset.filter(hall__cinema_id=cinema_id_param)

        user = self.request.user
        is_staff = user.is_authenticated and getattr(user, "role", None) in [
            "manager",
            "admin",
        ]
        if not is_staff:
            queryset = queryset.filter(date__gte=date.today())

        date_param = self.request.query_params.get("date")
        if date_param:
            queryset = queryset.filter(date=date_param)

        movie_id_param = self.request.query_params.get("movie_id")
        if movie_id_param:
            queryset = queryset.filter(movie_id=movie_id_param)

        return queryset

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return MovieSessionWriteSerializer
        if self.action == "retrieve":
            return MovieSessionReadSerializer
        return CompactMovieSessionReadSerializer
