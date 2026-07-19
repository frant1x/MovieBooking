from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("secret-panel/", admin.site.urls),
    path("users/", include("users.urls")),
    path("cinemas/", include("cinemas.urls")),
    path("movies/", include("movies.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
