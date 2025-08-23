from django.urls import path
from rest_framework.permissions import AllowAny

from users.apps import UsersConfig
from users.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    UserCreateAPIView,
    UserDestroyAPIView,
    UserListAPIView,
    UserRetrieveAPIView,
    UserUpdateAPIView, BusyEmployeesAPIView,
)

app_name = UsersConfig.name

urlpatterns = [
    path("register/", UserCreateAPIView.as_view(), name="register"),
    path("", UserListAPIView.as_view(), name="users-list"),
    path("<int:pk>/", UserRetrieveAPIView.as_view(), name="user-retrieve"),
    path(
        "<int:pk>/delete/",
        UserDestroyAPIView.as_view(),
        name="user-delete",
    ),
    path(
        "<int:pk>/update/",
        UserUpdateAPIView.as_view(),
        name="user-update",
    ),
    path(
        "login/",
        CustomTokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path(
        "token/refresh/",
        CustomTokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token-refresh",
    ),
    path('busy-employees/', BusyEmployeesAPIView.as_view(), name='busy-employees'),
]
