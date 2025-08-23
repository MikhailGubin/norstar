from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta

from tasks.models import Task
from users.models import User

class TaskTestCase(APITestCase):

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
            "owner": f"{self.user.id}",
            "executor": f"{self.other_user.id}",
            "task_name": "Создать модель Пользователь",
            "deadline": (timezone.now() + timedelta(days=7)).isoformat(),
        }


    def test_task_retrieve(self):
        """Проверяет процесс просмотра одного объекта класса "Задание" """
        url = reverse("tasks:task-retrieve", args=[self.task.pk])

        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("task_name"), self.task.task_name)
        self.assertEqual(data.get("owner"), self.user.id)

    def test_task_create(self):
        """Проверяет процесс создания одного объекта класса "Задание" """
        url = reverse("tasks:task-create")
        response = self.client.post(url, self.task_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.all().count(), 2)

        created_task = Task.objects.get(task_name=self.task_data["task_name"])
        self.assertEqual(created_task.executor, self.other_user)
        self.assertEqual(created_task.deadline.isoformat(), self.task_data["deadline"])
        self.assertEqual(created_task.owner, self.user)
        
    def test_delete_task_success(self):
        """Проверяет успешное удаление задания."""
        # Используем self.task (создана в setUp)
        url = reverse("tasks:task-delete", kwargs={"pk": self.task.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что привычка действительно удалена из базы данных
        self.assertFalse(Task.objects.filter(id=self.task.pk).exists())
        
    def test_create_task_validation_error_duration(self):
        """Проверяет создание задания с недопустимым сроком сдачи."""
        url = reverse("tasks:task-create")

        self.task_data["deadline"] = timezone.now().isoformat()
        response = self.client.post(url, self.task_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("deadline", response.json())
        self.assertIn(
            "Время сдачи выполненного задания должно превышать текущее время не менее, чем на 1 час",
            response.json()["deadline"]
        )
