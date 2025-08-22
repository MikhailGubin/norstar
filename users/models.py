from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Переопределяю модель 'Пользователь'"""

    POSITION_CHOICES = [
        ('', '---------'),  # Пустой вариант
        ('employee', 'Сотрудник'),
        ('team_leaders', 'Руководитель'),
        ('director', 'Директор'),
    ]

    username = None
    email = models.EmailField(unique=True, verbose_name="Почта", help_text="Укажите почту")
    avatar = models.ImageField(
        upload_to="users/avatars/",
        verbose_name="Аватар",
        blank=True,
        null=True,
        help_text="Загрузите свой аватар",
    )
    phone = models.CharField(
        max_length=35,
        verbose_name="Телефон",
        blank=True,
        null=True,
        help_text="Введите номер телефона",
    )
    city = models.CharField(
        max_length=50,
        verbose_name="Город",
        blank=True,
        null=True,
        help_text="Введите название города",
    )
    tg_chat_id = models.CharField(
        max_length=50,
        verbose_name="Телеграм chat-id",
        blank=True,
        null=True,
        help_text="Укажите телеграм chat-id",
    )
    position = models.CharField(
        max_length=100,
        choices=POSITION_CHOICES,
        blank=True,  # Разрешаем пустое значение
        default='',  # Значение по умолчанию
        verbose_name="Должность",
        help_text="Укажите должность",
    )
    surname = models.CharField(
        max_length=30,
        blank=True,
        default='',
        verbose_name="Фамилия",
        help_text="Укажите Фамилию",
    )
    name = models.CharField(
        max_length=30,
        blank=True,
        default='',
        verbose_name="Имя",
        help_text="Укажите имя",
    )
    patronymic = models.CharField(
        max_length=30,
        blank=True,
        default='',
        verbose_name="Отчество",
        help_text="Укажите отчество",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
