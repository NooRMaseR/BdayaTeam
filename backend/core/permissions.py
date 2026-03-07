from rest_framework.permissions import BasePermission
from .models import UserRole

class RolePermission(BasePermission):
    required_role: UserRole | None = None
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == self.required_role

class IsTechnical(RolePermission):
    required_role = UserRole.TECHNICAL
    message = f"Only {required_role}s are Allowed"
    
class IsOrganizer(RolePermission):
    required_role = UserRole.ORGANIZER
    message = f"Only {required_role}s are Allowed"
    
class IsMember(RolePermission):
    required_role = UserRole.MEMBER
    message = f"Only {required_role}s are Allowed"

class IsTechnicalOrOrganizer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == UserRole.TECHNICAL or request.user.role == UserRole.ORGANIZER)
    
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)

class IsTechnicalOrMember(BasePermission):
    message = "Only Technicals or Members are Allowed"
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == UserRole.TECHNICAL or request.user.role == UserRole.MEMBER)
    
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser
    
    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)