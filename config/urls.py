from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf.urls.static import static
from tasks import views
from config import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Norstar",
        default_version="v1",
        description="Данное веб-приложение является трекером задач для сотрудников",
        terms_of_service="https://MVGubin1323@yandex.ru/policies/terms/",
        contact=openapi.Contact(email="MVGubin1323@yandex.ru"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("", views.IndexList.as_view(), name="index"),
    path("admin/", admin.site.urls),
    path("tasks/", include("tasks.urls", namespace="tasks")),
    path("users/", include("users.urls", namespace="users")),
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
