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
        return obj.owner == request.user