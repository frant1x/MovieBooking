from rest_framework import serializers
from cinemas.serializers import CompactHallSerializer, HallSerializer, SeatSerializer
from .models import Movie, MovieSession
from orders.models import Ticket


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"


class CompactMovieSessionReadSerializer(serializers.ModelSerializer):
    hall = CompactHallSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = MovieSession
        fields = ["id", "movie", "hall", "date", "slot", "price"]


class MovieSessionReadSerializer(serializers.ModelSerializer):
    hall = HallSerializer(read_only=True)
    movie = MovieSerializer(read_only=True)
    seats = serializers.SerializerMethodField()

    class Meta:
        model = MovieSession
        fields = ["id", "movie", "hall", "seats", "date", "slot", "price"]

    def get_seats(self, obj):
        all_seats = obj.hall.seats.all()

        occupied_seat_ids = set(
            Ticket.objects.filter(moviesession=obj).values_list("seat_id", flat=True)
        )

        return SeatSerializer(
            all_seats,
            many=True,
            context={"occupied_seat_ids": occupied_seat_ids},
        ).data


class MovieSessionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieSession
        fields = ["id", "movie", "hall", "date", "slot", "price"]
