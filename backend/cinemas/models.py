from django.db import models


class Cinema(models.Model):
    """Model representing a cinema."""

    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.city})"


class Hall(models.Model):
    """Model representing a hall in a cinema."""

    class HallType(models.TextChoices):
        IMAX = "IMAX", "IMAX"
        FOURDX = "4DX", "4DX"
        CINETECH = "CINETECH+", "CINETECH+"
        RELUX = "RE'LUX", "RE'LUX"

    cinema = models.ForeignKey(Cinema, on_delete=models.CASCADE, related_name="halls")
    number = models.PositiveIntegerField()
    hall_type = models.CharField(
        max_length=50, choices=HallType.choices, default=HallType.CINETECH
    )
    rows_count = models.PositiveIntegerField()
    seats_per_row = models.PositiveIntegerField()

    class Meta:
        unique_together = ("cinema", "number")

    def __str__(self):
        return f"Зал {self.number}, {self.hall_type} ({self.cinema.name})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            self.generate_seats()

    def generate_seats(self):
        """Automatically generates seats for the hall."""
        seats_to_create = []

        for row in range(1, self.rows_count + 1):
            for seat_num in range(1, self.seats_per_row + 1):
                seats_to_create.append(
                    Seat(
                        hall=self,
                        row_number=row,
                        seat_number=seat_num,
                    )
                )

        Seat.objects.bulk_create(seats_to_create)


class Seat(models.Model):
    """Model representing a seat in a hall."""

    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name="seats")
    row_number = models.PositiveIntegerField()
    seat_number = models.PositiveIntegerField()

    class Meta:
        unique_together = ("hall", "row_number", "seat_number")
        ordering = ("row_number", "seat_number")

    def __str__(self):
        return f"Місце {self.row_number}-{self.seat_number} ({self.hall})"
