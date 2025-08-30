from django.urls import path

from tasks.apps import TasksConfig
from tasks.views import (
    TaskCreateAPIView,
    TaskDestroyAPIView,
    TaskOwnerListAPIView,
    TaskRetrieveAPIView,
    TaskUpdateAPIView,
    TaskListAPIView, ImportantTasksAPIView, BusyEmployeesAPIView,
)

app_name = TasksConfig.name

urlpatterns = [
    path("", TaskListAPIView.as_view(), name="tasks"),
    path("owners/", TaskOwnerListAPIView.as_view(), name="owner-tasks"),
    path("<int:pk>/", TaskRetrieveAPIView.as_view(), name="task-retrieve"),
    path("create/", TaskCreateAPIView.as_view(), name="task-create"),
    path("<int:pk>/delete/", TaskDestroyAPIView.as_view(), name="task-delete"),
    path("<int:pk>/update/", TaskUpdateAPIView.as_view(), name="task-update"),
    path('busy_employees/', BusyEmployeesAPIView.as_view(), name='busy-employees'),
    path('important_tasks/', ImportantTasksAPIView.as_view(), name='important-tasks'),
]
