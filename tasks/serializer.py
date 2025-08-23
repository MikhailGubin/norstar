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
        read_only_fields = ["owner", 'time_created', 'time_updated', 'time_started', 'time_completed']
        validators = [
            DeadlineValidator(field="deadline"),
        ]

        def validate(self, data):
            """ Проверка, что исполнитель не меняется для задачи в работе """
            instance = self.instance
            if instance and instance.status == Task.status.in_process:
                if 'executor' in data and data['executor'] != instance.executor:
                    raise serializers.ValidationError({
                        'executor': 'Нельзя менять исполнителя для задачи в работе'
                    })
            return data
