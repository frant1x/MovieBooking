from django.db import models
from cinemas.models import Hall


class Movie(models.Model):

    class Status(models.TextChoices):
        COMING_SOON = "upcoming", "Скоро в кіно"
        ACTIVE = "active", "В прокаті"
        ARCHIVE = "archived", "Архів"

    title = models.CharField(max_length=255)
    poster_url = models.ImageField(upload_to="posters/", blank=True, null=True)
    duration = models.PositiveIntegerField()
    release_date = models.DateField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    def __str__(self):
        return self.title


class MovieSession(models.Model):

    class SessionSlot(models.TextChoices):
        MORNING = "10:00", "10:00"
        AFTERNOON = "14:00", "14:00"
        EVENING = "18:00", "18:00"
        NIGHT = "22:00", "22:00"

    movie = models.ForeignKey(Movie, on_delete=models.PROTECT, related_name="sessions")
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT, related_name="sessions")
    date = models.DateField(default=None)
    slot = models.CharField(
        max_length=5, choices=SessionSlot.choices, default=SessionSlot.MORNING
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.movie.title} | {self.hall.cinema.name} (Зал {self.hall.number}) | {self.date} {self.slot}"

    class Meta:
        ordering = ["date", "slot"]
        unique_together = ("hall", "date", "slot")
