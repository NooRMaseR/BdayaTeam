from ninja_extra.permissions import BasePermission as NinjaBasePermission
from .models import UserRole

class NinjaRolePermission(NinjaBasePermission):
    required_role: UserRole | None = None
    
    def has_permission(self, request, controller) -> bool:
        return request.user.is_authenticated and request.user.role == self.required_role # type: ignore

class NinjaIsTechnical(NinjaRolePermission):
    required_role = UserRole.TECHNICAL
    message = f"Only {required_role}s are Allowed"
    
class NinjaIsOrganizer(NinjaRolePermission):
    required_role = UserRole.ORGANIZER
    message = f"Only {required_role}s are Allowed"
    
class NinjaIsMember(NinjaRolePermission):
    required_role = UserRole.MEMBER
    message = f"Only {required_role}s are Allowed"

class NinjaIsTechnicalOrOrganizer(NinjaBasePermission):
    message = "Only Technicals or Organizers are Allowed"
    
    def has_permission(self, request, controller) -> bool:
        return request.user.is_authenticated and (request.user.is_technical or request.user.is_organizer) # type: ignore

class NinjaIsTechnicalOrMember(NinjaBasePermission):
    message = "Only Technicals or Members are Allowed"
    
    def has_permission(self, request, controller) -> bool:
        return request.user.is_authenticated and (request.user.is_technical or request.user.is_member) # type: ignore

class NinjaIsSuperUser(NinjaBasePermission):
    def has_permission(self, request, controller) -> bool:
        return request.user.is_authenticated and request.user.is_superuser
    