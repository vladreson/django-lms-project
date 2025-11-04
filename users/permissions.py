from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """
    Права доступа для модераторов
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()

    def has_object_permission(self, request, view, obj):
        return request.user.groups.filter(name='moderators').exists()


class IsOwner(permissions.BasePermission):
    """
    Права доступа для владельцев объектов
    """
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsOwnerOrModerator(permissions.BasePermission):
    """
    Права доступа для владельцев или модераторов
    """
    def has_object_permission(self, request, view, obj):
        if request.user.groups.filter(name='moderators').exists():
            return True
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        return False


class IsNotModerator(permissions.BasePermission):
    """
    Права доступа для НЕ модераторов (обычные пользователи)
    """
    def has_permission(self, request, view):
        return not request.user.groups.filter(name='moderators').exists()