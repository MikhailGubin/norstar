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


class BusyEmployeesAPITestCase(APITestCase):

    def setUp(self):
        """Создание тестовых данных"""
        # Создание авторизованного пользователя
        self.user = User.objects.create(email="admin@example.com")
        self.user.set_password("12345")
        self.user.save()
        self.client.force_authenticate(user=self.user)
        
        # Создаем сотрудников
        self.user1 = User.objects.create(
            email="user1@example.com",
            name="Иван",
            surname="Иванов",
            patronymic="Иванович",
            position="Разработчик",
            password="45678",
        )

        self.user2 = User.objects.create(
            email="user2@example.com",
            name="Петр",
            surname="Петров",
            patronymic="Петрович",
            position="Аналитик",
            password="45678",
        )

        self.user3 = User.objects.create(
            email="user3@example.com",
            name="Сидор",
            surname="Сидоров",
            patronymic="Сидорович",
            position="Тестировщик",
            password="45678",
        )

        # Создаем задачи с разными статусами
        self.task1 = Task.objects.create(
            task_name="Активная задача 1",
            executor=self.user1,
            deadline=timezone.now() + timedelta(days=5),
            status=Task.Status.IN_PROCESS,
            owner=self.user,
        )

        self.task2 = Task.objects.create(
            task_name="Активная задача 2",
            executor=self.user1,
            deadline=timezone.now() + timedelta(days=3),
            status=Task.Status.UNDER_UNDER_REVIEW,
            owner = self.user,
        )

        self.task3 = Task.objects.create(
            task_name="Завершенная задача",
            executor=self.user2,
            deadline=timezone.now() + timedelta(days=1),
            status=Task.Status.COMPLETED,
            owner=self.user,
        )

        self.task4 = Task.objects.create(
            task_name="Активная задача 3",
            executor=self.user2,
            deadline=timezone.now() + timedelta(days=2),
            status=Task.Status.IN_PROCESS,
            owner=self.user,
        )

    def test_busy_employees_ordering(self):
        """Проверяет правильность сортировки по количеству активных задач"""
        url = reverse("tasks:busy-employees")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # user1: 2 активные задачи, user2: 1 активная задача, user3: 0 активных задач
        self.assertEqual(len(data), 4)
        self.assertEqual(data[0]['active_tasks_count'], 2)  # user1
        self.assertEqual(data[1]['active_tasks_count'], 1)  # user2
        self.assertEqual(data[2]['active_tasks_count'], 0)  # user3

        # Проверяем, что user1 первый в списке (наиболее загружен)
        self.assertEqual(data[0]['email'], 'user1@example.com')
        self.assertEqual(data[0]['active_tasks_count'], 2)
        self.assertEqual(data[0]['total_tasks_count'], 2)

    def test_busy_employees_data_structure(self):
        """Проверяет структуру возвращаемых данных"""
        url = reverse("tasks:busy-employees")
        response = self.client.get(url)
        data = response.json()

        # Проверяем наличие всех необходимых полей
        employee = data[0]
        self.assertIn('id', employee)
        self.assertIn('name', employee)
        self.assertIn('email', employee)
        self.assertIn('position', employee)
        self.assertIn('active_tasks_count', employee)
        self.assertIn('total_tasks_count', employee)

    def test_busy_employees_no_tasks(self):
        """Проверяет корректную работу при отсутствии задач"""
        Task.objects.all().delete()

        url = reverse("tasks:busy-employees")
        response = self.client.get(url)
        data = response.json()

        # Все сотрудники должны иметь 0 активных задач
        for employee in data:
            self.assertEqual(employee['active_tasks_count'], 0)
            self.assertEqual(employee['total_tasks_count'], 0)


class ImportantTasksAPITestCase(APITestCase):

    def setUp(self):
        """Создание сложной структуры задач для тестирования"""
        # Создание авторизованного пользователя
        self.user = User.objects.create(
            email="admin@example.com",
            name="Александр",
            surname="Александров",
            patronymic="Александрович",
            password = "12345",
        )
        self.user.set_password("12345")
        self.user.save()
        self.client.force_authenticate(user=self.user)
        # Создаем сотрудников
        self.user1 = User.objects.create(
            email="user1@example.com",
            name="Иван",
            surname="Иванов",
            patronymic="Иванович",
            position="Разработчик",
            password="12345",
        )

        self.user2 = User.objects.create(
            email="user2@example.com",
            name="Петр",
            surname="Петров",
            patronymic="Петрович",
            position="Аналитик",
            password="12345",
        )

        self.user3 = User.objects.create(
            email="user3@example.com",
            name="Сидор",
            surname="Сидоров",
            patronymic="Сидорович",
            position="Тестировщик",
            password="12345",
        )

        # Создаем родительские задачи (не в работе)
        self.parent_task1 = Task.objects.create(
            task_name="Родительская задача 1",
            owner=self.user,
            executor=self.user1,
            deadline=timezone.now() + timedelta(days=7),
            status=Task.Status.CREATED
        )

        self.parent_task2 = Task.objects.create(
            task_name="Родительская задача 2",
            owner=self.user,
            executor=self.user2,
            deadline=timezone.now() + timedelta(days=5),
            status=Task.Status.CREATED
        )

        # Создаем дочерние задачи (в работе)
        self.child_task1 = Task.objects.create(
            task_name="Дочерняя задача 1",
            owner=self.user,
            executor=self.user1,
            parent=self.parent_task1,
            deadline=timezone.now() + timedelta(days=3),
            status=Task.Status.IN_PROCESS
        )

        self.child_task2 = Task.objects.create(
            task_name="Дочерняя задача 2",
            owner=self.user,
            executor=self.user2,
            parent=self.parent_task1,
            deadline=timezone.now() + timedelta(days=2),
            status=Task.Status.UNDER_REVIEW
        )

        self.child_task3 = Task.objects.create(
            task_name="Дочерняя задача 3",
            owner=self.user,
            executor=self.user3,
            parent=self.parent_task2,
            deadline=timezone.now() + timedelta(days=1),
            status=Task.Status.IN_PROCESS
        )

        # Создаем независимую задачу (не должна попасть в важные)
        self.independent_task = Task.objects.create(
            task_name="Независимая задача",
            owner=self.user,
            executor=self.user1,
            deadline=timezone.now() + timedelta(days=4),
            status=Task.Status.CREATED
        )

    def test_important_tasks_filtering(self):
        """Проверяет правильность фильтрации важных задач"""
        url = reverse('tasks:important-tasks')
        response = self.client.get(url)
        data = response.json()
        # Проверяем, что эндпоинт доступен
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Должны найтись 2 важные задачи
        self.assertEqual(len(data), 2)

        # Проверяем, что независимая задача не попала в список
        task_names = [task['Важная задача'] for task in data]
        self.assertNotIn('Независимая задача', task_names)

        # Проверяем, что родительские задачи найдены
        self.assertIn('Родительская задача 1', task_names)
        self.assertIn('Родительская задача 2', task_names)

    def test_important_tasks_data_structure(self):
        """Проверяет структуру возвращаемых данных"""
        url = reverse('tasks:important-tasks')
        response = self.client.get(url)
        data = response.json()

        task = data[0]
        self.assertIn('Важная задача', task)
        self.assertIn('Срок до', task)
        self.assertIn('Возможные исполнители', task)
        # 'Возможные исполнители' должен быть списком
        self.assertIsInstance(task['Возможные исполнители'], list)

    def test_important_tasks_potential_executors(self):
        """Проверяет логику подбора потенциальных исполнителей"""
        url = reverse('tasks:important-tasks')
        response = self.client.get(url)
        data = response.json()

        # Для родительской задачи 1 (у user1 уже 1 активная задача)
        task1 = next(t for t in data if t['Важная задача'] == 'Родительская задача 1')

        # Должны быть предложены исполнители (user2 или user3 как менее загруженные)
        self.assertGreater(len(task1['Возможные исполнители']), 0)

        # Проверяем, что исполнитель текущей задачи не предлагается
        current_executor = f"{self.user1.surname} {self.user1.name} {self.user1.patronymic}"
        self.assertNotIn(current_executor, task1['Возможные исполнители'])

        # Проверяем, что другие исполнители предлагаются
        other_executor = f"{self.user3.surname} {self.user3.name} {self.user3.patronymic}"  # ФИО user3
        self.assertIn(other_executor, task1['Возможные исполнители'])

    def test_important_tasks_no_dependencies(self):
        """Проверяет работу при отсутствии зависимостей"""
        # Удаляем все дочерние задачи
        Task.objects.filter(parent__isnull=False).delete()

        url = reverse('tasks:important-tasks')
        response = self.client.get(url)
        data = response.json()

        # Не должно быть важных задач
        self.assertEqual(len(data), 0)
#
    def test_important_tasks_all_dependencies_completed(self):
        """Проверяет, что задачи с завершенными зависимостями не считаются важными"""
        # Меняем статус дочерних задач на "Выполнено"
        Task.objects.filter(parent__isnull=False).update(status=Task.Status.COMPLETED)

        url = reverse('tasks:important-tasks')
        response = self.client.get(url)
        data = response.json()

        # Не должно быть важных задач
        self.assertEqual(len(data), 0)
