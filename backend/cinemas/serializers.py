from rest_framework import serializers
from .models import Cinema, Hall, Seat


class CinemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cinema
        fields = "__all__"


class SeatSerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ["id", "row_number", "seat_number", "is_available"]

    def get_is_available(self, obj):
        occupied_seat_ids = self.context.get("occupied_seat_ids", set())
        return obj.id not in occupied_seat_ids


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
