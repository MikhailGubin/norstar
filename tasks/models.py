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
    is_important = models.BooleanField(
        default=False,
        verbose_name="Признак важной задачи",
        help_text="Определяет является ли задача важной, т.е. зависят ли от неё другие задачи",
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name="Признак главной задачи",
        help_text="Определяет является ли задача главной, т.е. есть ли у неё дочерние задачи",
    )
    related_task = models.ForeignKey(
        "self",  # Ссылка на саму себя
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Связанная задача",
        help_text="Укажите задачу, выполнение которой связано с реализацией данной задачи.",
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        # Уникальность связки пользователь-действие-время-место, если нужно избежать дубликатов
        unique_together = ("owner", "executor", "task_name", "deadline")

    def __str__(self):
        return (f"Задача: {self.task_name},\nАвтор задачи: {self.owner.email},\nИсполнитель: {self.executor.email},\n"
                f"Срок выполнения: до {self.deadline}")
