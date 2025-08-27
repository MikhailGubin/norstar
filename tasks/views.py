from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from tasks.models import Task
from tasks.pagination import TasksPagination
from tasks.serializer import TaskSerializer
from tasks.services import EmployeeService, TaskService
from users.permissions import IsSupervisor, IsOwner


class TaskCreateAPIView(CreateAPIView):
    """Создаёт объект класса 'Задание'"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (~IsSupervisor, IsAuthenticated)

    @swagger_auto_schema(operation_summary="task-create")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Добавляет текущего пользователя в поле "Владелец" модели "Задание" """
        task = serializer.save(owner=self.request.user)
        task.owner = self.request.user
        task.save()


class TaskOwnerListAPIView(ListAPIView):
    """Передаёт список заданий текущего Пользователя с пагинацией"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = TasksPagination

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(owner=user)
        else:
            return Task.objects.none()


class TaskListAPIView(ListAPIView):
    """Передаёт список заданий"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = TasksPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="supervisor").exists():
            return Task.objects.all()
        elif user.is_authenticated:
            return Task.objects.filter(executor=user)
        else:
            return Task.objects.none()


class TaskRetrieveAPIView(RetrieveAPIView):
    """Передаёт представление определённого объекта класса 'Задание'"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (~IsSupervisor, IsAuthenticated)


class TaskUpdateAPIView(UpdateAPIView):
    """Меняет информацию в представлении объекта класса 'Задание'"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (~IsSupervisor, IsAuthenticated)

    @swagger_auto_schema(
        operation_summary="task-full-update",
        operation_description="Полностью обновляет данные существующего задания.",
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="task-patch", operation_description="Частично обновляет данные существующего задания."
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class TaskDestroyAPIView(DestroyAPIView):
    """Удаляет объект класса 'Задание'"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    @swagger_auto_schema(operation_summary="task-delete")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class BusyEmployeesAPIView(APIView):
    """Список сотрудников с количеством активных задач"""

    permission_classes = (~IsSupervisor, IsAuthenticated)

    def get(self, request):
        data = EmployeeService.get_busy_employees()
        return Response(data)

class ImportantTasksAPIView(APIView):
    """Важные задачи и рекомендуемые исполнители"""

    permission_classes = (~IsSupervisor, IsAuthenticated)

    def get(self, request):
        result = TaskService.get_important_tasks_with_suggestions()
        return Response(result)
