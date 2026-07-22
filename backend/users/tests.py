from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserAPITestCase(APITestCase):

    def setUp(self):
        self.user_data = {
            "name": "test",
            "email": "test@email.com",
            "password": "test",
        }
        self.user = User.objects.create_user(**self.user_data)

        self.user_url = reverse("user-list")
        self.login_url = reverse("login")
        self.my_page_url = reverse("user-me")

    def test_register_user_success(self):
        body = {
            "name": "new user",
            "email": "new_user@email.com",
            "password": "newuser",
        }
        response = self.client.post(self.user_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="new_user@email.com").exists())

    def test_register_user_duplicate_email(self):
        body = {
            "name": "new user",
            "email": "test@email.com",
            "password": "newuser",
        }
        response = self.client.post(self.user_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(name="new user").exists())

    def test_login_user_success(self):
        body = {
            "email": "test@email.com",
            "password": "test",
        }
        response = self.client.post(self.login_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_invalid_password(self):
        body = {
            "email": "test@email.com",
            "password": "invalid",
        }
        response = self.client.post(self.login_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.my_page_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_get_profile_unauthorized(self):
        response = self.client.get(self.my_page_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        self.client.force_authenticate(user=self.user)
        body = {"name": "updated"}
        response = self.client.patch(self.my_page_url, body, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "updated")

    def test_delete_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.my_page_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_get_users_info(self):
        response = self.client.get(self.user_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
