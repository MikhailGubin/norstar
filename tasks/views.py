from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from tasks.models import Task
from tasks.serializer import TaskSerializer


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

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.is_authenticated:
    #         return Task.objects.filter(owner=user)
    #     else:
    #         return Task.objects.none()


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

