from rest_framework import permissions


class AuthorPermission(permissions.IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        if request.method in ("PATCH", "DELETE"):
            return obj.author == request.user
        return request.method in permissions.SAFE_METHODS
