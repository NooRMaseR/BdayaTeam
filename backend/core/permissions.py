from ninja_extra.permissions import BasePermission as NinjaBasePermission
from .models import UserRole


import jwt
from django_bolt import Request
from django.conf import settings
from .models import BdayaUser, UserRole
from django_bolt.exceptions import Unauthorized, Forbidden

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
    
    
def require_role(role_label: str, allowed_jwt_roles: list[UserRole]):
    """
    A Dependency Factory that builds a specific security gatekeeper.
    """
    
    # This inner function is what Bolt actually executes
    async def security_dependency(request: Request) -> BdayaUser:
        token = request.cookies.get('access_token')
        
        if not token:
            auth_header = request.headers.get('authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            raise Unauthorized(detail="Missing authentication token")

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            if payload.get('role') not in allowed_jwt_roles:
                raise Forbidden(detail=f"Only {role_label} are Allowed")

            user_id = payload.get('user_id')

            user = await (
                BdayaUser.objects
                .defer("track__prefix", "is_staff", "joined_at", "last_login", "track__en_description", "track__ar_description", "track__image", "member__joined_at", "member__status")
                .select_related("track", 'member')
                .aget(id=user_id)
            )
            
            return user

        except jwt.ExpiredSignatureError:
            raise Unauthorized(detail="Token expired")
        except jwt.InvalidTokenError:
            raise Unauthorized(detail="Invalid token")
            
    return security_dependency

# Exact Roles
get_org_user    = require_role("Organizers", [UserRole.ORGANIZER])
get_tech_user   = require_role("Technicals", [UserRole.TECHNICAL])
get_member_user = require_role("Members",    [UserRole.MEMBER])

# Combined Roles
get_tech_or_org_user    = require_role("Technicals or Organizers", [UserRole.TECHNICAL, UserRole.ORGANIZER])
get_tech_or_member_user = require_role("Technicals or Members",    [UserRole.TECHNICAL, UserRole.MEMBER])

# A baseline auth for any valid user
get_any_authenticated_user = require_role("Authenticated Users", [UserRole.TECHNICAL, UserRole.ORGANIZER, UserRole.MEMBER])
