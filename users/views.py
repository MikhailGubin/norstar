from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.permissions import IsAuthenticated

from users.models import User
from users.pagination import UsersPagination
from users.serializer import UserSerializer
from users.permissions import IsSupervisor, IsOwner


class UserCreateAPIView(CreateAPIView):
    """Контроллер для регистрации пользователей"""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, IsSupervisor)

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        user.is_active = True
        user.save()

    @swagger_auto_schema(
        operation_id="user_register",
        operation_summary="Создание нового Пользователя"
    )
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class UserListAPIView(ListAPIView):
    """Передаёт представления объектов класса 'Пользователь'"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UsersPagination
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        operation_id="users",
        operation_summary="Список Пользователей",
        responses={
            200: UserSerializer(many=True),
            400: "Неверные параметры запроса"
        }
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserRetrieveAPIView(RetrieveAPIView):
    """Передаёт представление определённого объекта класса 'Пользователь'"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(operation_id="user_retrieve")
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class UserUpdateAPIView(UpdateAPIView):
    """Меняет информацию в представлении объекта класса 'Пользователь'"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsSupervisor | IsOwner )

    @swagger_auto_schema(
        operation_id="user_full_update",
        operation_summary="Полностью обновляет данные о Пользователе."
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_id="user_partial_update",
        operation_summary="Частично обновляет данные о Пользователе."
    )
    def patch(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class UserDestroyAPIView(DestroyAPIView):
    """Удаляет объект класса 'Пользователь'"""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsSupervisor)

    @swagger_auto_schema(
        operation_id="user_delete",
        operation_summary="Удаление Пользователя"
    )
    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):

    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        operation_id="user_token_refresh",
        operation_summary="Обновляет пару access/refresh токенов, используя валидный refresh токен.",
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

    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        operation_id="user_login",
        operation_summary="Позволяет пользователю аутентифицироваться, используя имя пользователя и пароль, "
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
        return super().post(request, *args, **kwargs)
