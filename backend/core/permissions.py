from typing import Any
from .models import UserRole
from .models import BdayaUser, UserRole
from django_bolt import JWTAuthentication, Requires


IsSuperUser = Requires('is_superuser', True)
IsOrganizer = Requires('role', UserRole.ORGANIZER, message="Only Organizers Are Allowed")
IsTechnical = Requires('role', UserRole.TECHNICAL, message="Only Technicals Are Allowed")
IsMember = Requires('role', UserRole.MEMBER, message="Only Members Are Allowed")
IsTechnicalOrOrganizer = Requires('role', UserRole.TECHNICAL, UserRole.ORGANIZER, message="Only Technicals or Organizers Are Allowed")
IsTechnicalOrMember = Requires('role', UserRole.TECHNICAL, UserRole.MEMBER, message="Only Technicals or Members Are Allowed")


class JWTCookiesAuthentication(JWTAuthentication):
    async def get_user(self, user_id: str | None, auth_context: dict[str, Any]) -> BdayaUser:
        return await (
            BdayaUser.objects.defer(
                "track__prefix",
                "joined_at",
                "last_login",
                "track__en_description",
                "track__ar_description",
                "track__image",
                "member__joined_at",
                "member__status",
            )
            .select_related("track", "member")
            .aget(id=user_id)
        )
    
    def get_user_sync(self, user_id: str | None) -> Any | None:
        return (
            BdayaUser.objects.defer(
                "track__prefix",
                "joined_at",
                "last_login",
                "track__en_description",
                "track__ar_description",
                "track__image",
                "member__joined_at",
                "member__status",
            )
            .select_related("track", "member")
            .get(id=user_id)
        )
