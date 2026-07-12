from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ("email", "role")
    list_filter = ("role",)
    search_fields = ("email", "name")
    ordering = ("email",)
    readonly_fields = ("created_at", "updated_at", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональна інформація", {"fields": ("name", "role")}),
        (
            "Права доступу",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        (
            "Важливі дати",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                    "last_login",
                )
            },
        ),
    )

    # Налаштування форми СТВОРЕННЯ НОВОГО користувача (саме тут відбувається магія хешування)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("collapse",),
                "fields": ("email", "name", "role", "password"),
            },
        ),
    )


# Реєструємо нашу модель разом із кастомним класом адмінки
admin.site.register(User, CustomUserAdmin)
