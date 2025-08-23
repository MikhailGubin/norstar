from django.db import models


class Task(models.Model):
    """Модель 'Задание'"""

    STATUS_CHOICES = [
        ('created', 'создана'),
        ('needs_clarification', 'требует уточнения'),
        ('in_process', 'в работе'),
        ('under_review', 'на проверке'),
        ('completed', 'выполнена'),
        ('cancelled', 'отменена'),
    ]

    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="Автор задания",
        help_text="Укажите автора задания",
        related_name="tasks",
    )
    executor = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        verbose_name="Исполнитель",
        help_text="Укажите исполнителя задания",
    )
    task_name = models.CharField(
        max_length=200,
        verbose_name="Наименование задачи",
        help_text="Укажите наименование задачи",
    )
    deadline = models.DateTimeField(
        verbose_name="Срок выполнения",
        help_text="Укажите время, до которого нужно выполнить задачу",
    )
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        blank=True,  # Разрешаем пустое значение
        default='created',  # Значение по умолчанию
        verbose_name="Статус задания",
        help_text="Укажите статус задания",
    )
    priority = models.IntegerField(
        default=1,
        choices=[(1, 'Низкий'), (2, 'Средний'), (3, 'Высокий')],
        verbose_name="Приоритет",
        help_text="Укажите приоритет задания",
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
        verbose_name="Родительская задача",
        help_text="Укажите родительскую задачу"
    )
    time_created = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_updated = models.DateTimeField(auto_now=True, verbose_name="Время обновления")
    time_started = models.DateTimeField(null=True, blank=True, verbose_name="Время начала работы")
    time_completed = models.DateTimeField(null=True, blank=True, verbose_name="Время завершения")
    description = models.TextField(
        blank=True,
        default='',
        verbose_name="Описание",
        help_text="Укажите описание задачи"
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        # Уникальность совокупности полей, если нужно избежать дубликатов
        unique_together = ("owner", "executor", "task_name", "deadline")

    def __str__(self):
        return (f"Задача: {self.task_name},\nАвтор задачи: {self.owner.email},\nИсполнитель: {self.executor.email},\n"
                f"Срок выполнения: до {self.deadline}")
