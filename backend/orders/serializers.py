from rest_framework import serializers
from .models import Ticket, Order
from movies.models import MovieSession
from cinemas.models import Seat
from movies.serializers import CompactMovieSessionReadSerializer
from django.db import transaction


class TicketSerializer(serializers.ModelSerializer):
    moviesession = CompactMovieSessionReadSerializer(read_only=True)
    row_number = serializers.ReadOnlyField(source="seat.row_number")
    seat_number = serializers.ReadOnlyField(source="seat.seat_number")

    class Meta:
        model = Ticket
        fields = [
            "id",
            "moviesession",
            "row_number",
            "seat_number",
        ]


class OrderReadSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_price",
            "created_at",
            "tickets",
        ]


class OrderCreateSerializer(serializers.Serializer):
    moviesession_id = serializers.PrimaryKeyRelatedField(
        queryset=MovieSession.objects.all(), source="moviesession", write_only=True
    )
    seat_ids = serializers.PrimaryKeyRelatedField(
        queryset=Seat.objects.all(), many=True, source="seats", write_only=True
    )

    def validate(self, attrs):
        moviesession = attrs["moviesession"]
        seats = attrs["seats"]

        if not seats:
            raise serializers.ValidationError(
                {"seat_ids": "Need to provide at least one seat ID."}
            )

        if len(seats) != len(set(seats)):
            raise serializers.ValidationError(
                {"seat_ids": "Duplicate seats found in request."}
            )

        hall_seat_ids = set(moviesession.hall.seats.values_list("id", flat=True))
        for seat in seats:
            if seat.id not in hall_seat_ids:
                raise serializers.ValidationError(
                    f"Seat with ID {seat.id} does not belong to the hall of this session."
                )

        occupied_seat_ids = Ticket.objects.filter(
            moviesession=moviesession, seat__in=seats
        ).values_list("seat_id", flat=True)

        if occupied_seat_ids:
            raise serializers.ValidationError(
                "One or more selected seats are already reserved for this session."
            )

        return attrs

    def create(self, validated_data):
        moviesession = validated_data["moviesession"]
        seats = validated_data["seats"]
        user = validated_data["user"]

        price_per_ticket = moviesession.price
        total_price = price_per_ticket * len(seats)

        with transaction.atomic():
            order = Order.objects.create(
                user=user,
                total_price=total_price,
                status=Order.Status.PENDING,
            )

            tickets = [
                Ticket(
                    order=order,
                    moviesession=moviesession,
                    seat=seat,
                    price=price_per_ticket,
                )
                for seat in seats
            ]
            Ticket.objects.bulk_create(tickets)

        return order

    def to_representation(self, instance):
        return OrderReadSerializer(instance, context=self.context).data
