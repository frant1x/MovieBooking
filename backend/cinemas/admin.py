from django.contrib import admin
from .models import Cinema, Hall, Seat


@admin.register(Cinema)
class CinemaAdmin(admin.ModelAdmin):
    list_display = ("name", "city")
    search_fields = ("name", "city")


@admin.register(Hall)
class HallAdmin(admin.ModelAdmin):
    list_display = ("number", "hall_type", "cinema")
    list_filter = ("hall_type", "cinema")
    ordering = ("cinema",)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["rows_count", "seats_per_row"]
        return []


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("hall", "row_number", "seat_number")
    list_filter = ("hall__cinema", "hall")
    ordering = ("hall", "row_number", "seat_number")

    def get_readonly_fields(self, request, obj=None):
        """Захист: у створеного крісла не можна випадково змінити його координати"""
        if obj:
            return ["hall", "row_number", "seat_number"]
        return []
