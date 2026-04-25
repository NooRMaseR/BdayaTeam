import jwt
from utils import STORE
from .models import UserRole
from django_bolt import Request
from django.conf import settings
from .models import BdayaUser, UserRole
from django_bolt.exceptions import Unauthorized, Forbidden, BadRequest

def require_role(role_label: str, allowed_jwt_roles: list[UserRole]):
    """
    A Dependency Factory that builds a specific security gatekeeper.
    """
    
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
            
            jti = payload.get("jti")
            if not jti:
                raise Unauthorized(detail="Invalid Token")
            
            if await STORE.is_revoked(jti):
                raise Unauthorized(detail="Token is revoked")
            
            if payload.get('role') not in allowed_jwt_roles:
                raise Forbidden(detail=f"Only {role_label} are Allowed")

            user_id = payload.get('sub')

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
        except BdayaUser.DoesNotExist:
            raise BadRequest(detail=f"User with id does not exists")
            
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
