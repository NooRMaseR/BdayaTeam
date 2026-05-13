from phonenumber_field.validators import validate_international_phonenumber
from django_bolt.serializers import Serializer, field_validator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django_bolt import UploadFile

from organizer.serializers import SiteSettingsImagesMSGSerializer
from .serializers import TrackNameOnlyMSGSerializer
from . import models, validators
import msgspec

class LoginRequestMSG(msgspec.Struct):
    email: str
    password: str

class LoginResponseMSG(msgspec.Struct):
    username: str
    is_admin: bool
    role: models.UserRole
    track: TrackNameOnlyMSGSerializer | None = None

class RegisterRequestMSG(Serializer):
    request_track_id: int
    email: str
    name: str
    phone_number: str
    collage_code: str
    
    @field_validator('email', 'before')
    def validate_email(cls, v: str) -> str:
        try:
            validate_email(v)
        except ValidationError as e:
            error = e.message if hasattr(e, 'message') else e.messages[0]
            raise ValueError(error)

        return v
    
    @field_validator('collage_code', 'before')
    def validate_collage(cls, v: str) -> str:
        try:
            validators.validate_collage_code(v)
        except ValidationError as e:
            error = e.message if hasattr(e, 'message') else e.messages[0]
            raise ValueError(error)
        
        return v
    
    @field_validator('phone_number', 'before')
    def validate_phone(cls, v: str) -> str:
        try:
            validate_international_phonenumber(v)
        except ValidationError as e:
            error = e.message if hasattr(e, 'message') else e.messages[0]
            raise ValueError(error)
        
        return v
    
class RefreshTokenRequestMSG(msgspec.Struct):
    refresh: str | None = None

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

class TrackCreateRequestMSG(msgspec.Struct):
    name: str
    prefix: str
    en_description: str
    ar_description: str
    image: UploadFile
