from rest_framework import serializers
from cinemas.serializers import HallSerializer
from .models import Movie, MovieSession


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"


class MovieSessionReadSerializer(serializers.ModelSerializer):
    hall = HallSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = MovieSession
        fields = ["id", "movie", "hall", "date", "slot", "price"]


class MovieSessionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieSession
        fields = ["id", "movie", "hall", "date", "slot", "price"]
