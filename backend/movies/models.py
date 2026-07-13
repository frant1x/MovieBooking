from django.db import models
from cinemas.models import Hall


class Movie(models.Model):
    title = models.CharField(max_length=255)
    poster_url = models.URLField(blank=True, null=True)
    duration = models.PositiveIntegerField()
    release_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title


class MovieSession(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.PROTECT, related_name="sessions")
    hall = models.ForeignKey(Hall, on_delete=models.PROTECT, related_name="sessions")
    start_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        formatted_time = self.start_time.strftime("%d.%m %H:%M")
        return f"{self.movie.title} | {self.hall.cinema.name} (Зал {self.hall.number}) | {formatted_time}"

    class Meta:
        ordering = ["start_time"]
