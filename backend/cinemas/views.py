from rest_framework import viewsets
from .models import Cinema
from .serializers import CinemaSerializer


class CinemaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cinema.objects.all()
    serializer_class = CinemaSerializer
