from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from rest_framework.response import Response

from tasks.models import Task
from tasks.serializer import TaskSerializer
from users.models import User


class TaskCreateAPIView(CreateAPIView):
    """Создаёт объект класса 'Задание'"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    # permission_classes = (IsAuthenticated,)

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
    # pagination_class = CustomPagination

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_authenticated:
    #         return Task.objects.filter(is_public=True)
    #     else:
    #         return Task.objects.none()


class TaskRetrieveAPIView(RetrieveAPIView):
    """Передаёт представление определённого объекта класса 'Задание'"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    # permission_classes = (IsAuthenticated, IsOwner)


class TaskUpdateAPIView(UpdateAPIView):
    """Меняет информацию в представлении объекта класса 'Задание'"""

    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    # permission_classes = (
    #     IsAuthenticated,
    #     IsOwner,
    # )

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
    # permission_classes = (IsAuthenticated, IsOwner)

    @swagger_auto_schema(operation_summary="task-delete")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ImportantTasksAPIView(APIView):
    """Важные задачи и рекомендуемые исполнители"""

    def get(self, request):
        # 1. Находим важные задачи
        important_tasks = Task.objects.filter(
            status=Task.status.created,  # Не взяты в работу
            subtasks__status__in=[Task.status.in_process, Task.status.under_review]  # Зависимости в работе
        ).distinct()

        # 2. Получаем статистику загрузки сотрудников
        from users.models import User
        employee_stats = User.objects.annotate(
            active_tasks_count=Count('tasks', filter=Q(tasks__status__in=[
                Task.status.in_process, Task.status.under_review
            ]))
        ).values('id', 'active_tasks_count')

        # Находим минимальную загрузку
        min_load = min([stat['active_tasks_count'] for stat in employee_stats], default=0)

        result = []
        for task in important_tasks:
            # 3. Находим потенциальных исполнителей
            potential_executors = []

            # Вариант 1: Исполнитель родительской задачи
            if task.parent and task.parent.executor:
                parent_executor = task.parent.executor
                executor_load = next(
                    (stat['active_tasks_count'] for stat in employee_stats
                     if stat['id'] == parent_executor.id), 0
                )
                if executor_load <= min_load + 2:  # Не более чем на 2 задачи больше
                    potential_executors.append(parent_executor.get_full_name())

            # Вариант 2: Наименее загруженные сотрудники
            least_loaded_employees = User.objects.annotate(
                active_tasks_count=Count('tasks', filter=Q(tasks__status__in=[
                    Task.status.in_process, Task.status.under_review
                ]))
            ).filter(active_tasks_count__lte=min_load + 2).order_by('active_tasks_count')

            for employee in least_loaded_employees[:3]:  # Топ-3 наименее загруженных
                if employee.get_full_name() not in potential_executors:
                    potential_executors.append(employee.get_full_name())

            result.append({
                'task_id': task.id,
                'task_name': task.name,
                'deadline': task.deadline,
                'potential_executors': potential_executors,
                'dependency_count': task.subtasks.filter(
                    status__in=[Task.status.in_process, Task.status.under_review]
                ).count()
            })

        return Response(result)

