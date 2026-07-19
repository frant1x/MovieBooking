from django.contrib import admin
from .models import Movie, MovieSession


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_date", "status")
    search_fields = ("title",)
    list_filter = ("release_date", "status")


@admin.register(MovieSession)
class MovieSessionAdmin(admin.ModelAdmin):
    list_display = ("movie", "hall", "date", "slot")
    search_fields = ("movie__title",)
    list_filter = ("date", "slot")
    ordering = ("date", "slot")
