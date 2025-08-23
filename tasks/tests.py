from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta

from tasks.models import Task
from users.models import User

class HabitTestCase(APITestCase):

    def setUp(self):
        """Создает базовый набор параметров для тестов для модели "Задание" """
        # Создание Пользователя
        self.user = User.objects.create(email="admin@example.com")
        self.user.set_password("12345")
        self.user.save()
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

        # Создание тестового задания
        self.task = Task.objects.create(
            owner=self.user,
            executor=self.other_user,
            task_name="Создать модель Объект",
            deadline=(timezone.now() + timedelta(days=7)).isoformat(),
        )
        self.task_data = {
            "executor": self.other_user.id,
            "task_name": "Создать модель Объект",
            "deadline": (timezone.now() + timedelta(days=7)).isoformat(),
        }


    def test_habit_retrieve(self):
        """Проверяет процесс просмотра одного объекта класса "Привычка" """
        url = reverse("tasks:task-retrieve", args=[self.task.pk])

        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("task_name"), self.task.task_name)
        self.assertEqual(data.get("owner"), self.user.id)