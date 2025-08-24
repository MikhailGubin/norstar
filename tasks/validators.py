from datetime import timedelta

from rest_framework.serializers import ValidationError
from django.utils import timezone

from tasks.models import Task


class DeadlineValidator:
    """ Проверяет, что время сдачи выполненного задания не может быть раньше, чем через час после создания задания """
    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        time_finished = dict(value).get(self.field)
        time_now = timezone.now()
        if time_finished is None:
            raise ValidationError(
                {"deadline": "Укажите время выполнения задания"}
            )
        if time_finished < (time_now + timedelta(hours=1)):  # duration - это минуты
            raise ValidationError({"deadline":
               "Время сдачи выполненного задания должно превышать текущее время не менее, чем на 1 час"})


class ParentTaskValidator:
    """Проверяет корректность родительской задачи"""

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        parent = dict(value).get(self.field)
        if parent and parent.status == Task.Status.COMPLETED:
            raise ValidationError(
                "Нельзя назначить родительской задачей уже выполненную задачу"
            )


class ExecutorTaskValidator:

    def __init__(self, field, instance):
        self.field = field
        self.instance = instance

    def __call__(self, value):
        executor = value
        if self.instance and self.instance.status == Task.Status.IN_PROCESS:
            if executor and executor != self.instance.executor:
                raise ValidationError({
                    'executor': 'Нельзя менять исполнителя для задачи в работе'
                })
