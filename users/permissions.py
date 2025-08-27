from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Проверяет, является ли пользователь владельцем
    """

    message = "Вы не являетесь автором задания"

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsSupervisor(permissions.BasePermission):
    """
    Проверяет, является ли пользователь руководителем
    """

    message = "Вы не состоите в группе руководителей"

    def has_permission(self, request, view):
        return request.user.groups.filter(name="supervisor").exists()
