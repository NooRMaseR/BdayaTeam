from phonenumber_field.validators import validate_international_phonenumber
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from organizer.serializers import SiteSettingsImagesMSGSerializer
from .serializers import TrackNameOnlyMSGSerializer
from . import models, validators
from typing import Annotated
import msgspec

class LoginRequestMSG(msgspec.Struct):
    email: str
    password: str

class LoginResponseMSG(msgspec.Struct):
    username: str
    is_admin: bool
    role: models.UserRole
    track: TrackNameOnlyMSGSerializer | None = None

class RegisterRequestMSG(msgspec.Struct):
    request_track_id: Annotated[int, msgspec.Meta(gt=0)]
    email: str
    name: str
    phone_number: str
    collage_code: str
    
    def __post_init__(self) -> None:
        try:
            validate_email(self.email)
        except ValidationError as e:
            error = e.message if hasattr(e, 'message') else e.messages[0]
            raise msgspec.ValidationError(f"email: {error}")

        try:
            validators.validate_collage_code(self.collage_code)
        except ValidationError as e:
            error = e.message if hasattr(e, 'message') else e.messages[0]
            raise msgspec.ValidationError(f"collage_code: {error}")

        try:
            validate_international_phonenumber(self.phone_number)
        except ValidationError as e:
            error = e.message if hasattr(e, 'message') else e.messages[0]
            raise msgspec.ValidationError(f"phone_number: {error}")
    
class RefreshTokenRequestMSG(msgspec.Struct):
    refresh: str | None = None

class TrackCreateMSG(msgspec.Struct):
    name: str
    prefix: str
    en_description: str
    ar_description: str

class RegisterResponseMSG(msgspec.Struct):
    code: str
    track: TrackNameOnlyMSGSerializer
    email: str
    name: str

class TestAuthResponseMSG(msgspec.Struct):    
    username: str
    role: models.UserRole
    is_admin: bool
    settings: SiteSettingsImagesMSGSerializer
    track: TrackNameOnlyMSGSerializer | None = None
