from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    def has_permission(self, request, view):
        """
        Проверка, является ли пользователь модератором
        """
        return request.user.groups.filter(name="Moderators").exists()


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Проверка, является ли пользователь владельцем
        """
        return obj.owner == request.user


class IsCurrentUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Проверка, является ли текущий пользователь владельцем учетной записи
        """
        return obj == request.user
