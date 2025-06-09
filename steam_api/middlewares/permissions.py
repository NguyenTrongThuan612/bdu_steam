from rest_framework import permissions
from steam_api.models.web_user import WebUserRole

class IsRoot(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == WebUserRole.ROOT

class IsNotRoot(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role != WebUserRole.ROOT
    
class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == WebUserRole.MANAGER
    
class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == WebUserRole.TEACHER