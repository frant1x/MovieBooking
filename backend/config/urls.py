from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("secret-panel/", admin.site.urls),
    path("users/", include("users.urls")),
    path("cinemas/", include("cinemas.urls")),
    path("movies/", include("movies.urls")),
]
