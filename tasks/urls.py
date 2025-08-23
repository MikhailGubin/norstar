from django.urls import path

from tasks.apps import TasksConfig
from tasks.views import (
    TaskCreateAPIView,
    TaskDestroyAPIView,
    TaskOwnerListAPIView,
    TaskRetrieveAPIView,
    TaskUpdateAPIView,
    TaskListAPIView, ImportantTasksAPIView,
)

app_name = TasksConfig.name

urlpatterns = [
    path("", TaskListAPIView.as_view(), name="tasks-list"),
    path("owner_list/", TaskOwnerListAPIView.as_view(), name="owner-tasks-list"),
    path("<int:pk>/", TaskRetrieveAPIView.as_view(), name="task-retrieve"),
    path("create/", TaskCreateAPIView.as_view(), name="task-create"),
    path("<int:pk>/delete/", TaskDestroyAPIView.as_view(), name="task-delete"),
    path("<int:pk>/update/", TaskUpdateAPIView.as_view(), name="task-update"),
    path('important-tasks/', ImportantTasksAPIView.as_view(), name='important-tasks'),
]
