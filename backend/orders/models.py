from django.db import models
from users.models import User
from movies.models import MovieSession
from cinemas.models import Seat


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Очікує оплати"
        PAID = "PAID", "Оплачено"
        EXPIRED = "EXPIRED", "Час вичерпано"
        CANCELLED = "CANCELLED", "Скасовано"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Замовлення {self.id} - {self.user} - {self.status}"


class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")
    moviesession = models.ForeignKey(
        MovieSession, on_delete=models.CASCADE, related_name="tickets"
    )
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT, related_name="tickets")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ("moviesession", "seat")

    def __str__(self):
        return f"{self.moviesession} - {self.seat}"
