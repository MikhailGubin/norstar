from rest_framework import serializers

from tasks.models import Task
from tasks.validators import DeadlineValidator, ParentTaskValidator, ExecutorTaskValidator


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
        read_only_fields = ["owner", 'time_created', 'time_updated', 'time_started', 'time_completed']
        validators = [
            DeadlineValidator(field="deadline"),
            ParentTaskValidator(field="parent"),
        ]


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["executor"].validators.append(
            ExecutorTaskValidator(field="executor", instance=self.instance)
        )
