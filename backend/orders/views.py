from rest_framework import viewsets, status
from .models import Order, Ticket
from .serializers import TicketSerializer, OrderReadSerializer, OrderCreateSerializer
from rest_framework.permissions import IsAuthenticated
from datetime import date
from rest_framework.decorators import action
from rest_framework.response import Response


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing tickets."""

    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Ticket.objects.select_related(
            "moviesession__movie",
            "moviesession__hall__cinema",
            "seat",
        ).filter(order__user=user, order__status=Order.Status.PAID)

        ticket_type = self.request.query_params.get("type")
        if ticket_type == "archive":
            return queryset.filter(moviesession__date__lt=date.today())

        return queryset.filter(moviesession__date__gte=date.today())


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing orders."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.prefetch_related(
            "tickets__moviesession__movie",
            "tickets__moviesession__hall__cinema",
            "tickets__seat",
        )

        is_staff = user.is_authenticated and getattr(user, "role", None) in [
            "manager",
            "admin",
        ]
        if is_staff:
            return queryset.all()

        return queryset.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderReadSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel_order(self, request, pk=None):
        """
        Custom action to cancel an order.
        """
        order = self.get_object()

        if order.status != Order.Status.PENDING:
            return Response(
                {"detail": "Only pending orders can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = Order.Status.CANCELLED
        order.save()

        order.tickets.all().delete()

        return Response(
            {"detail": "Order successfully cancelled, seats released."},
            status=status.HTTP_200_OK,
        )
