from rest_framework.permissions import BasePermission
from .models import UserRole

class RoleRequired(BasePermission):
    required_role: UserRole | None = None
    
    def has_permission(self, request, view):
        return request.user.role == self.required_role
    
class IsTechnical(RoleRequired):
    required_role = UserRole.TECHNICAL
    message = f"Only {required_role}s are Allowed"
    
    
class IsOrganizer(RoleRequired):
    required_role = UserRole.ORGANIZER
    message = f"Only {required_role}s are Allowed"
    
    
class IsMember(RoleRequired):
    required_role = UserRole.MEMBER
    message = f"Only {required_role}s are Allowed"
    
