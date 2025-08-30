from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User
from django.contrib.auth.models import Group


class UserTestCase(APITestCase):

    def setUp(self):
        """Создает базовый набор параметров для тестов для модели "habit" """
        # Создаем группу supervisor
        self.supervisor_group, created = Group.objects.get_or_create(name='supervisor')

        # Создание Пользователя
        self.user = User.objects.create(
            email="admin@example.com",
            name="Александр",
            surname="Александров",
            patronymic="Александрович",
            password="12345",
            position="team_leader",
        )
        # Добавляем пользователя в группу supervisor
        self.user.groups.add(self.supervisor_group)
        self.user.save()
        # Авторизуем пользователя
        self.client.force_authenticate(user=self.user)

        # Создание другого сотрудника
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
        self.assertEqual(len(data["results"]), 2)

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

    def test_delete_user_success(self):
        """Проверяет успешное удаление Пользователя"""

        url = reverse("users:user-delete", kwargs={"pk": self.other_user.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что Пользователь удален из базы данных
        self.assertFalse(User.objects.filter(id=self.other_user.pk).exists())


class UserDeleteAuthTestCase(APITestCase):
        """Комплексные тесты аутентификации при удалении Пользователя"""

        def setUp(self):
            # Создаем группу supervisor
            self.supervisor_group, created = Group.objects.get_or_create(name='supervisor')

            self.supervisor_user = User.objects.create(
                email='supervisor@example.com',
                password='pass123',
                name='Руководитель',
                surname='Проекта',
                position='team_lead',
            )
            # Добавляем пользователя в группу supervisor
            self.supervisor_user.groups.add(self.supervisor_group)
            self.supervisor_user.save()

            # Создаем тестовых пользователей
            self.regular_user = User.objects.create(
                email='regular@example.com',
                password='pass123',
                name='Обычный',
                surname='Сотрудник',
                position='developer'
            )

            self.url = reverse("users:user-delete", kwargs={"pk": self.regular_user.pk})

        def test_unauthenticated_user_cannot_delete_user(self):
            """Неавторизованный пользователь получает ошибку авторизации"""

            response = self.client.delete(self.url)

            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(response.json()['detail'], 'Authentication credentials were not provided.')

        def test_regular_user_cannot_delete_user(self):
            """Обычный пользователь получает 403 ошибку"""
            self.client.force_authenticate(user=self.regular_user)

            response = self.client.delete(self.url)

            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(response.json()['detail'], 'Вы не состоите в группе руководителей')
