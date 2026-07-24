from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from cinemas.models import Cinema, Hall
from movies.models import Movie, MovieSession
from orders.models import Order, Ticket
from users.models import User, UserRole


class MovieAPITestCase(APITestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
            name="customer",
            email="customer@email.com",
            password="customer",
            role=UserRole.CUSTOMER,
        )
        self.manager = User.objects.create_user(
            name="manager",
            email="manager@email.com",
            password="manager",
            role=UserRole.MANAGER,
        )

        self.movie_active = Movie.objects.create(
            title="test_active",
            duration=123,
            status=Movie.Status.ACTIVE,
        )

        self.movie_archive = Movie.objects.create(
            title="test_archive",
            duration=123,
            status=Movie.Status.ARCHIVE,
        )

        self.list_url = reverse("movie-list")
        self.detail_url = reverse("movie-detail", kwargs={"pk": self.movie_active.id})

    def test_get_movies_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_movies_by_status_success(self):
        params = {"status": "active"}
        response = self.client.get(self.list_url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], self.movie_active.title)

    def test_filter_movies_by_fake_status_success(self):
        params = {"status": "fake"}
        response = self.client.get(self.list_url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_customer_cannot_create_movie(self):
        self.client.force_authenticate(user=self.customer)

        body = {
            "title": "new movie",
            "duration": 123,
            "status": Movie.Status.ACTIVE,
        }
        response = self.client.post(self.list_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Movie.objects.filter(title="new movie").exists())

    def test_manager_can_create_movie(self):
        self.client.force_authenticate(user=self.manager)

        body = {
            "title": "new movie",
            "duration": 123,
            "status": Movie.Status.ACTIVE,
        }
        response = self.client.post(self.list_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Movie.objects.filter(title="new movie").exists())

    def test_get_movie_info(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.movie_active.title)

    def test_customer_cannot_update_movie(self):
        self.client.force_authenticate(user=self.customer)

        body = {"title": "updated", "status": Movie.Status.ARCHIVE}
        response = self.client.patch(self.detail_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Movie.objects.filter(title="updated").exists())

    def test_manager_can_update_movie(self):
        self.client.force_authenticate(user=self.manager)

        body = {"title": "updated", "status": Movie.Status.ARCHIVE}
        response = self.client.patch(self.detail_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.movie_active.refresh_from_db()
        self.assertEqual(self.movie_active.title, "updated")


class MovieSessionAPITestCase(APITestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
            name="customer",
            email="customer@email.com",
            password="customer",
            role=UserRole.CUSTOMER,
        )
        self.manager = User.objects.create_user(
            name="manager",
            email="manager@email.com",
            password="manager",
            role=UserRole.MANAGER,
        )

        self.cinema1 = Cinema.objects.create(name="test cinema1", city="test city1")
        self.cinema2 = Cinema.objects.create(name="test cinema2", city="test city2")

        self.hall1 = Hall.objects.create(
            cinema=self.cinema1,
            number=1,
            hall_type=Hall.HallType.CINETECH,
            rows_count=2,
            seats_per_row=2,
        )
        self.hall2 = Hall.objects.create(
            cinema=self.cinema2,
            number=1,
            hall_type=Hall.HallType.IMAX,
            rows_count=2,
            seats_per_row=2,
        )

        self.seat1 = self.hall1.seats.get(row_number=1, seat_number=1)
        self.seat2 = self.hall1.seats.get(row_number=2, seat_number=2)

        self.movie1 = Movie.objects.create(
            title="test1", duration=123, status=Movie.Status.COMING_SOON
        )
        self.movie2 = Movie.objects.create(
            title="test2", duration=123, status=Movie.Status.ARCHIVE
        )

        self.future_session = MovieSession.objects.create(
            movie=self.movie1,
            hall=self.hall1,
            date=date.today() + timedelta(days=2),
            slot=MovieSession.SessionSlot.MORNING,
            price=200,
        )

        self.past_session = MovieSession.objects.create(
            movie=self.movie2,
            hall=self.hall1,
            date=date.today() - timedelta(days=2),
            slot=MovieSession.SessionSlot.AFTERNOON,
            price=150,
        )

        self.other_cinema_session = MovieSession.objects.create(
            movie=self.movie1,
            hall=self.hall2,
            date=date.today() + timedelta(days=1),
            slot=MovieSession.SessionSlot.EVENING,
            price=220,
        )

        order = Order.objects.create(
            user=self.customer, total_price=200, status=Order.Status.PAID
        )
        Ticket.objects.create(
            order=order, moviesession=self.future_session, seat=self.seat1, price=200
        )

        self.list_url = reverse("moviesession-list")
        self.detail_url = reverse(
            "moviesession-detail", kwargs={"pk": self.future_session.id}
        )

        self.maxDiff = None

    def test_get_sessions_list_success(self):
        params = {"cinema_id": self.cinema1.id}
        response = self.client.get(self.list_url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.future_session.id)

        expected_output = {
            "id": self.future_session.id,
            "movie": {
                "id": self.movie1.id,
                "title": "test1",
                "poster_url": None,
                "duration": 123,
                "release_date": None,
                "status": "upcoming",
            },
            "hall": {
                "id": self.hall1.id,
                "cinema_name": "test cinema1",
                "number": 1,
                "hall_type": "CINETECH+",
            },
            "date": "2026-07-25",
            "slot": "10:00",
            "price": "200.00",
        }

        self.assertEqual(response.data[0], expected_output)

    def test_get_sessions_list_without_cinema_id(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_can_see_past_sessions(self):
        self.client.force_authenticate(user=self.manager)

        params = {"cinema_id": self.cinema1.id}
        response = self.client.get(self.list_url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_sessions_filter_by_date(self):
        self.client.force_authenticate(user=self.manager)

        params = {
            "cinema_id": self.cinema1.id,
            "date": str(date.today() + timedelta(days=2)),
        }
        response = self.client.get(self.list_url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.future_session.id)

    def test_list_sessions_filter_by_date(self):
        self.client.force_authenticate(user=self.manager)

        params = {
            "cinema_id": self.cinema1.id,
            "movie_id": self.movie2.id,
        }
        response = self.client.get(self.list_url, params)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["movie"]["title"], self.movie2.title)

    def test_get_session_detail(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.future_session.id)

        expected_output = {
            "id": self.future_session.id,
            "movie": {
                "id": self.movie1.id,
                "title": "test1",
                "poster_url": None,
                "duration": 123,
                "release_date": None,
                "status": "upcoming",
            },
            "hall": {
                "id": self.hall1.id,
                "cinema": {
                    "id": self.cinema1.id,
                    "name": "test cinema1",
                    "city": "test city1",
                    "address": "",
                },
                "number": 1,
                "hall_type": "CINETECH+",
            },
            "seats": [
                {
                    "id": self.hall1.seats.get(row_number=1, seat_number=1).id,
                    "row_number": 1,
                    "seat_number": 1,
                    "is_available": False,
                },
                {
                    "id": self.hall1.seats.get(row_number=1, seat_number=2).id,
                    "row_number": 1,
                    "seat_number": 2,
                    "is_available": True,
                },
                {
                    "id": self.hall1.seats.get(row_number=2, seat_number=1).id,
                    "row_number": 2,
                    "seat_number": 1,
                    "is_available": True,
                },
                {
                    "id": self.hall1.seats.get(row_number=2, seat_number=2).id,
                    "row_number": 2,
                    "seat_number": 2,
                    "is_available": True,
                },
            ],
            "date": "2026-07-25",
            "slot": "10:00",
            "price": "200.00",
        }

        self.assertEqual(response.data, expected_output)

    def test_get_session_detail_calculates_seat_availability(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("seats", response.data)

        seats = response.data["seats"]
        self.assertEqual(len(seats), 4)

        s1_data = next(s for s in seats if s["id"] == self.seat1.id)
        s2_data = next(s for s in seats if s["id"] == self.seat2.id)

        self.assertFalse(s1_data["is_available"])
        self.assertTrue(s2_data["is_available"])

    def test_customer_cannot_create_session(self):
        self.client.force_authenticate(user=self.customer)

        body = {
            "movie": self.movie1.id,
            "hall": self.hall1.id,
            "date": str(date.today()),
            "price": 322,
        }
        response = self.client.post(self.list_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(MovieSession.objects.filter(price=322).exists())

    def test_manager_can_create_session(self):
        self.client.force_authenticate(user=self.manager)

        body = {
            "movie": self.movie1.id,
            "hall": self.hall1.id,
            "date": str(date.today()),
            "price": 322,
        }
        response = self.client.post(self.list_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(MovieSession.objects.filter(price=322).exists())

    def test_manager_can_update_session(self):
        self.client.force_authenticate(user=self.manager)

        body = {"slot": MovieSession.SessionSlot.AFTERNOON, "price": 210}
        response = self.client.patch(self.detail_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.future_session.refresh_from_db()
        self.assertEqual(self.future_session.slot, MovieSession.SessionSlot.AFTERNOON)
        self.assertEqual(self.future_session.price, 210.00)

    def test_manager_can_delete_session(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            MovieSession.objects.filter(id=self.future_session.id).exists()
        )
