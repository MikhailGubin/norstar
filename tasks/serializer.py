from rest_framework import serializers

from tasks.models import Task
from tasks.validators import DeadlineValidator


class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели "Задание" с кастомными валидаторами.
    """

    class Meta:
        model = Task

        fields = [
            "id",
            "owner",
            "executor",
            "task_name",
            "deadline",
            "status",
            "priority",
            "parent",
            "time_created",
            "time_updated",
            "time_started",
            "time_completed",
            "description"
        ]
        read_only_fields = ["owner"]
        validators = [
            DeadlineValidator(field="deadline"),
        ]
