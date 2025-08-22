from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserTestCase(APITestCase):

    def setUp(self):
        """Создает базовый набор параметров для тестов для модели "habit" """
        # Создание Пользователя
        self.user = User.objects.create(email="admin@example.com")
        self.user.set_password("12345")
        self.user.save()
        self.client.force_authenticate(user=self.user)


        # Создание другого Пользователя
        self.other_user = User.objects.create(
            email="other_user@example.com",
            password="45678",
            surname="Иванов",
            name="Иван",
            patronymic="Иванович",
            position="employee",
        )
        self.other_user.save()

    def test_list_users(self):
        """Проверяет получение списка пользователей."""
        url = reverse("users:users-list")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 2)

    def test_user_retrieve(self):
        """Проверяет процесс просмотра одного объекта класса "Пользователь" """
        url = reverse("users:user-retrieve", args=[self.user.pk])
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.user.name)
        self.assertEqual(data.get("email"), self.user.email)

    def test_update_user_patch_success(self):
        """Проверяет успешное частичное редактирование пользователя (PATCH)."""
        url = reverse("users:user-update", kwargs={"pk": self.user.pk})
        new_data = {
            "name": "Петр",
        }
        response = self.client.patch(url, new_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("name"), "Петр")
        # Проверяем, что другие поля остались прежними
        self.assertEqual(response.json().get("surname"), self.user.surname)
