from rest_framework import serializers

from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Habit с кастомными валидаторами.
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
            "is_important",
            "is_main",
            "related_task",
        ]
        read_only_fields = ["owner"]

    # --- Валидация на уровне объекта (методы validate) ---
    # def validate(self, data):
    #     """Валидация на уровне объекта для проверки взаимосвязи полей."""
    #     # data содержит данные, которые пришли в запросе.
    #     # self.instance содержит существующий объект, если это PUT/PATCH запрос.
    #     # Получаем значения полей, учитывая, что в PATCH-запросе их может не быть
    #     is_pleasant = data.get("is_pleasant", self.instance.is_pleasant if self.instance else False)
    #     reward = data.get("reward", self.instance.reward if self.instance else None)
    #     related_habit = data.get("related_habit", self.instance.related_habit if self.instance else None)
    #     duration = data.get("duration", self.instance.duration if self.instance else None)
    #     periodicity_days = data.get("periodicity_days", self.instance.periodicity_days if self.instance else None)
    #
    #     # 1. Исключить одновременный выбор связанной привычки и указания вознаграждения.
    #     validate_choose_reward_or_related_habit(is_pleasant, reward, related_habit)
    #
    #     # 2. У приятной привычки не может быть вознаграждения или связанной привычки.
    #     validate_pleasant_habit_without_reward_and_related_habit(is_pleasant, reward, related_habit)
    #
    #     # 3. В связанные привычки могут попадать только привычки с признаком приятной привычки.
    #     validate_related_habit_must_be_pleasant(related_habit)
    #
    #     # 4. Время выполнения полезных привычек должно быть не больше 120 секунд.
    #     validate_duration_for_useful_habit(duration, is_pleasant)
    #
    #     # 5. Нельзя выполнять полезную привычку реже, чем 1 раз в 7 дней.
    #     validate_periodicity_for_habit(periodicity_days, is_pleasant)
    #
    #     return data
