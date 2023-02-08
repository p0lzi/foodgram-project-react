from rest_framework import permissions


class IsAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Если пользователь авторизован и админ, то даем права на редактирования.
    Во всех остальных случаях даем доступ на просмотр.
    """

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin'
        return request.method in permissions.SAFE_METHODS


class IsCustomAdminUser(permissions.IsAuthenticated):
    """ Права для супер-юзера или пользователя с ролью администратора. """

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.role == 'admin'


class IsUserOrAdmin(permissions.IsAuthenticated):
    """ Права для проверки является пользователь владельцем объекта. """

    def has_object_permission(self, request, view, obj):
        return request.user.username == obj.username
