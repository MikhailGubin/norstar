from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.models import User
from users.serializer import UserSerializer


class UserCreateAPIView(CreateAPIView):
    """Контроллер для регистрации пользователей"""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        user.is_active = True
        user.save()

    @swagger_auto_schema(operation_summary="users_register")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class UserListAPIView(ListAPIView):
    """Передаёт представления объектов класса 'Пользователь'"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveAPIView(RetrieveAPIView):
    """Передаёт представление определённого объекта класса 'Пользователь'"""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserUpdateAPIView(UpdateAPIView):
    """Меняет информацию в представлении объекта класса 'Пользователь'"""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_summary="users_full_update", operation_description="Полностью обновляет данные о Пользователе."
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="users_patch", operation_description="Частично обновляет данные о Пользователе."
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class UserDestroyAPIView(DestroyAPIView):
    """Удаляет объект класса 'Пользователь'"""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(operation_summary="users_delete")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    @swagger_auto_schema(
        operation_summary="users_token_refresh",
        operation_description="Обновляет пару access/refresh токенов, используя валидный refresh токен.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Валидный refresh токен"),
            },
            required=["refresh"],
        ),
        responses={
            200: openapi.Response(
                description="Новая пара токенов",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING, description="Новый access токен"),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Обновленный refresh токен"),
                    },
                ),
            ),
            401: "Неверное имя пользователя или пароль",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        operation_summary="users_token_obtain",
        operation_description="Позволяет пользователю аутентифицироваться, используя имя пользователя и пароль, "
        "и получить access/refresh токены.",
        # Описание тела запроса (request_body)
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Имя пользователя"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="Пароль пользователя"),
            },
            required=["username", "password"],  # Указываем обязательные поля
        ),
        # Описание ответов
        responses={
            200: openapi.Response(
                description="Успешная аутентификация, токены возвращены",
                schema=openapi.Schema(  # Описываем структуру ответа
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(type=openapi.TYPE_STRING, description="Access токен"),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh токен"),
                    },
                ),
            ),
            401: "Неверное имя пользователя или пароль (Unauthorized)",
            400: "Некорректные данные в запросе (Bad Request)",
        },
    )
    def post(self, request, *args, **kwargs):
        """
        Переопределяем метод post для применения декоратора swagger_auto_schema.
        """
        return super().post(request, *args, **kwargs)
