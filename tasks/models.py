from django.utils import timezone
from django.db import models
from rest_framework.serializers import ValidationError

class Task(models.Model):
    """Модель 'Задание'"""

    class Status(models.TextChoices):
        CREATED = 'created', 'создана'
        NEEDS_CLARIFICATION = 'needs_clarification', 'требует уточнения'
        IN_PROCESS = 'in_process', 'в работе'
        UNDER_REVIEW = 'under_review', 'на проверке'
        COMPLETED = 'completed', 'выполнена'
        CANCELLED = 'cancelled', 'отменена'

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
        choices=Status.choices,
        default=Status.CREATED,
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

    def clean(self):
        """Валидация на уровне модели"""
        errors = {}

        # Валидация родительской задачи (защита от циклических зависимостей)
        if self.parent:
            current = self.parent
            while current:
                if current == self:
                    errors['parent'] = 'Нельзя создать циклическую зависимость задач'
                    break
                current = current.parent

        # Валидация статусов
        if self.status == self.Status.IN_PROCESS and not self.time_started:
            self.time_started = timezone.now()

        if self.status == self.Status.COMPLETED and not self.time_completed:
            self.time_completed = timezone.now()

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()  # Вызов валидации
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        """Задача считается активной, если она в работе или на проверке"""
        return self.status in [
            self.Status.IN_PROCESS,
            self.Status.UNDER_REVIEW,
            self.Status.NEEDS_CLARIFICATION
        ]

    @property
    def is_final(self):
        """Задача в конечном статусе"""
        return self.status in [
            self.Status.COMPLETED,
            self.Status.CANCELLED
        ]

    @property
    def has_active_dependencies(self):
        """Есть ли активные зависимые задачи"""
        return self.subtasks.filter(status__in=[Task.Status.IN_PROCESS, Task.Status.UNDER_REVIEW]).exists()
