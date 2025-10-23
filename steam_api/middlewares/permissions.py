from rest_framework import permissions
from steam_api.models.web_user import WebUserRole
import logging

class IsRoot(permissions.BasePermission):
    def has_permission(self, request, view):
        has_permission = request.user.role == WebUserRole.ROOT

        if not has_permission:
            logging.getLogger().debug("IsRoot.has_permission user_id=%s, user_email=%s, role=%s", request.user.id, request.user.email, request.user.role)

        return has_permission

class IsNotRoot(permissions.BasePermission):
    def has_permission(self, request, view):
        has_permission = request.user.role != WebUserRole.ROOT

        if not has_permission:
            logging.getLogger().debug("IsNotRoot.has_permission user_id=%s, user_email=%s, role=%s", request.user.id, request.user.email, request.user.role)

        return has_permission
    
class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        has_permission = request.user.role == WebUserRole.MANAGER

        if not has_permission:
            logging.getLogger().debug("IsManager.has_permission user_id=%s, user_email=%s, role=%s", request.user.id, request.user.email, request.user.role)

        return has_permission
    
class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        has_permission = request.user.role == WebUserRole.TEACHER

        if not has_permission:
            logging.getLogger().debug("IsTeacher.has_permission user_id=%s, user_email=%s, role=%s", request.user.id, request.user.email, request.user.role)

        return has_permission