from rest_framework import serializers
from .models import Cinema, Hall, Seat


class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = "__all__"


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = "__all__"


class HallSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)
    cinema = CinemaSerializer(read_only=True)

    class Meta:
        model = Hall
        fields = [
            "id",
            "cinema",
            "number",
            "hall_type",
            "seats",
        ]


class CompactHallSerializer(serializers.ModelSerializer):
    cinema_name = serializers.ReadOnlyField(source="cinema.name")

    class Meta:
        model = Hall
        fields = ["id", "cinema_name", "number", "hall_type"]
