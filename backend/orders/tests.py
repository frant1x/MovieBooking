from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cinemas.models import Cinema, Hall
from movies.models import Movie, MovieSession
from orders.models import Order, Ticket
from users.models import UserRole

User = get_user_model()


class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            name="customer1",
            email="customer1@email.com",
            password="customer1",
            role=UserRole.CUSTOMER,
        )

        self.cinema = Cinema.objects.create(name="cinema", city="city")
        self.hall = Hall.objects.create(
            cinema=self.cinema,
            number=1,
            hall_type=Hall.HallType.CINETECH,
            rows_count=2,
            seats_per_row=2,
        )
        self.seat1 = self.hall.seats.get(row_number=1, seat_number=1)
        self.seat2 = self.hall.seats.get(row_number=1, seat_number=2)
        self.seat3 = self.hall.seats.get(row_number=2, seat_number=1)

        self.movie = Movie.objects.create(
            title="movie",
            duration=166,
            status=Movie.Status.ACTIVE,
        )
        self.active_session = MovieSession.objects.create(
            movie=self.movie,
            hall=self.hall,
            date=date.today() + timedelta(days=1),
            price=200.00,
        )

        self.order = Order.objects.create(
            user=self.customer, total_price=200.00, status=Order.Status.PAID
        )
        self.ticket = Ticket.objects.create(
            order=self.order,
            moviesession=self.active_session,
            seat=self.seat1,
            price=200,
        )

        self.orders_list_url = reverse("order-list")
        self.order_detail_url = reverse("order-detail", kwargs={"pk": self.order.id})

    def test_get_orders_list_success(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.orders_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.order.id)

        expected_order_keys = {"id", "status", "total_price", "created_at", "tickets"}
        self.assertTrue(expected_order_keys.issubset(response.data[0].keys()))

    def test_customer_sees_only_own_orders(self):
        other_customer = User.objects.create_user(
            name="customer2",
            email="customer2@email.com",
            password="customer2",
            role=UserRole.CUSTOMER,
        )

        self.client.force_authenticate(user=self.customer)

        order = Order.objects.create(
            user=other_customer, total_price=200, status=Order.Status.PAID
        )
        Ticket.objects.create(
            order=order,
            moviesession=self.active_session,
            seat=self.seat2,
            price=200,
        )

        response = self.client.get(self.orders_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_manager_sees_all_orders(self):
        manager = User.objects.create_user(
            name="manager",
            email="manager@email.com",
            password="manager",
            role=UserRole.MANAGER,
        )
        self.client.force_authenticate(user=manager)

        response = self.client.get(self.orders_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.order.id)

    def test_create_order_success(self):
        self.client.force_authenticate(user=self.customer)

        body = {
            "moviesession_id": self.active_session.id,
            "seat_ids": [self.seat2.id, self.seat3.id],
        }
        response = self.client.post(self.orders_list_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Order.Status.PENDING)
        self.assertEqual(float(response.data["total_price"]), 400.00)
        self.assertTrue(
            Order.objects.filter(user=self.customer, total_price=400.00).exists()
        )
        self.assertEqual(Ticket.objects.count(), 3)

    def test_create_order_empty_seats(self):
        self.client.force_authenticate(user=self.customer)

        body = {
            "moviesession_id": self.active_session.id,
            "seat_ids": [],
        }
        response = self.client.post(self.orders_list_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("seat_ids", response.data)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_create_order_seat_from_another_hall(self):
        self.client.force_authenticate(user=self.customer)

        another_hall = Hall.objects.create(
            cinema=self.cinema,
            number=2,
            hall_type=Hall.HallType.IMAX,
            rows_count=2,
            seats_per_row=2,
        )
        seat = another_hall.seats.get(row_number=1, seat_number=1)

        body = {
            "moviesession_id": self.active_session.id,
            "seat_ids": [seat.id],
        }
        response = self.client.post(self.orders_list_url, body)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_create_order_occupied_seat_fails(self):
        self.client.force_authenticate(user=self.customer)

        body = {
            "moviesession_id": self.active_session.id,
            "seat_ids": [self.seat1.id, self.seat2.id],
        }
        response = self.client.post(self.orders_list_url, body)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            Order.objects.filter(user=self.customer, total_price=400.00).exists()
        )
        self.assertEqual(Ticket.objects.count(), 1)

    def test_create_order_for_past_session(self):
        self.client.force_authenticate(user=self.customer)

        past_session = MovieSession.objects.create(
            movie=self.movie,
            hall=self.hall,
            date=date.today() - timedelta(days=1),
            price=200.00,
        )

        body = {
            "moviesession_id": past_session.id,
            "seat_ids": [self.seat1.id],
        }
        response = self.client.post(self.orders_list_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("moviesession_id", response.data)
        self.assertEqual(Ticket.objects.count(), 1)

    def test_get_order_detail(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(self.order_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.order.id)

        expected_order_keys = {"id", "status", "total_price", "created_at", "tickets"}
        self.assertTrue(expected_order_keys.issubset(response.data.keys()))

    def test_cancel_order_success(self):
        self.client.force_authenticate(user=self.customer)

        pending_order = Order.objects.create(
            user=self.customer, total_price=200, status=Order.Status.PENDING
        )
        ticket = Ticket.objects.create(
            order=pending_order,
            moviesession=self.active_session,
            seat=self.seat2,
            price=123,
        )

        order_cancel_url = reverse(
            "order-cancel-order", kwargs={"pk": pending_order.id}
        )
        response = self.client.post(order_cancel_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        pending_order.refresh_from_db()
        self.assertEqual(pending_order.status, Order.Status.CANCELLED)
        self.assertFalse(Ticket.objects.filter(id=ticket.id).exists())

    def test_cancel_non_pending_order_fails(self):
        self.client.force_authenticate(user=self.customer)

        order_cancel_url = reverse("order-cancel-order", kwargs={"pk": self.order.id})
        response = self.client.post(order_cancel_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PAID)
        self.assertTrue(Ticket.objects.filter(id=self.ticket.id).exists())
