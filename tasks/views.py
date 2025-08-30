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
    permission_classes = (IsSupervisor, IsAuthenticated)

    @swagger_auto_schema(
        operation_id="task_create",
        operation_summary="Создание нового задания"
    )
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Добавляет текущего пользователя в поле 'Владелец'"""
        task = serializer.save(owner=self.request.user)
        task.save()


class TaskOwnerListAPIView(ListAPIView):
    """Передаёт список заданий текущего Пользователя с пагинацией"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = TasksPagination

    @swagger_auto_schema(
        operation_id="owners",
        operation_summary="Список заданий, созданных данным пользователем",
        responses={
            200: TaskSerializer(many=True),
            400: "Неверные параметры запроса"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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

    @swagger_auto_schema(
        operation_id="tasks",
        operation_summary="Список заданий. Для работников видны только их задания. Для руководителей видны все задания",
        responses={
            200: TaskSerializer(many=True),
            400: "Неверные параметры запроса"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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
    permission_classes = (IsSupervisor, IsAuthenticated)

    @swagger_auto_schema(operation_id="task_retrieve")
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class TaskUpdateAPIView(UpdateAPIView):
    """Меняет информацию в представлении объекта класса 'Задание'"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsSupervisor, IsAuthenticated)

    @swagger_auto_schema(
        operation_id="task_full_update",
        operation_summary="Полное обновление задачи"
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="task_partial_update",
        operation_summary="Частичное обновление задачи"
    )
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class TaskDestroyAPIView(DestroyAPIView):
    """Удаляет объект класса 'Задание'"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    @swagger_auto_schema(
        operation_id="task_delete",
        operation_summary="Удаление задачи"
                         )
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class BusyEmployeesAPIView(APIView):
    """Список сотрудников с количеством активных задач"""

    permission_classes = (IsSupervisor, IsAuthenticated)
    pagination_class = TasksPagination

    @swagger_auto_schema(
        operation_id="busy_employees",
        operation_summary="Список сотрудников с количеством активных задач",
        responses={
            200: TaskSerializer(many=True),
            400: "Неверные параметры запроса"
        }
    )
    def get(self, request):
        data = EmployeeService.get_busy_employees()
        return Response(data)

class ImportantTasksAPIView(APIView):
    """Важные задачи и рекомендуемые исполнители"""

    permission_classes = (IsSupervisor, IsAuthenticated)
    pagination_class = TasksPagination

    @swagger_auto_schema(
        operation_id="important_tasks",
        operation_summary="Список важных задач и рекомендуемых исполнителей",
        responses={
            200: TaskSerializer(many=True),
            400: "Неверные параметры запроса"
        }
    )
    def get(self, request):
        result = TaskService.get_important_tasks_with_suggestions()
        return Response(result)
