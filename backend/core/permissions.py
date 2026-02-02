from rest_framework.permissions import BasePermission
from .models import UserRole

class RoleRequired(BasePermission):
    required_role: UserRole | None = None
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == self.required_role
    
class IsTechnical(RoleRequired):
    required_role = UserRole.TECHNICAL
    message = f"Only {required_role}s are Allowed"
    
class IsOrganizer(RoleRequired):
    required_role = UserRole.ORGANIZER
    message = f"Only {required_role}s are Allowed"
    
class IsMember(RoleRequired):
    required_role = UserRole.MEMBER
    message = f"Only {required_role}s are Allowed"    

class IsTechnicalOrOrganizer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == UserRole.TECHNICAL or request.user.role == UserRole.ORGANIZER)

class IsTechnicalOrMember(BasePermission):
    message = "Only Technicals or Members are Allowed"
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == UserRole.TECHNICAL or request.user.role == UserRole.MEMBER)

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser