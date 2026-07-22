from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders.views import TicketViewSet, OrderViewSet

router = DefaultRouter()
router.register(r"tickets", TicketViewSet, basename="ticket")
router.register(r"", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]
