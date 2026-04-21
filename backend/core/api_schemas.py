from typing import Annotated

from django_bolt.serializers import Serializer
from phonenumber_field.validators import validate_international_phonenumber
from pydantic import EmailStr, PositiveInt, field_validator
from core.serializers import TrackNameOnlyMSGSerializer
from organizer.api_schemas import SettingsImagesResponse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from organizer.serializers import SiteSettingsImagesMSGSerializer
from . import models, validators
from ninja import Schema
import msgspec

class DetailError(Schema):
    error: str
    
class PydanticErrorItem(Schema):
    type: str
    loc: list[str | int]
    msg: str
    ctx: DetailError

class PydanticErrorResponse(Schema):
    detail: list[PydanticErrorItem]

class LoginRequest(Schema):
    email: EmailStr
    password: str
    
class LoginRequestMSG(msgspec.Struct):
    email: str
    password: str

class LoginResponseMSG(msgspec.Struct):
    username: str
    is_admin: bool
    role: models.UserRole
    track: TrackNameOnlyMSGSerializer | None = None

class LoginResponse(Schema):
    username: str
    is_admin: bool
    role: models.UserRole
    track: SimpleTrackSchema | None = None

class ErrorResponse(Schema):
    details: str

class SingleErrorResponse(Schema):
    detail: str

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
    
class RegisterRequest(Schema):
    request_track_id: PositiveInt
    email: EmailStr
    name: str
    phone_number: str
    collage_code: str

    @field_validator("collage_code")
    @classmethod
    def check_collage_code(cls, v: str) -> str:
        try:
            validators.validate_collage_code(v)
            return v
        except ValidationError as e:
            error = e.message if hasattr(e, 'message') else e.messages[0]
            raise ValueError(error)
    
    @field_validator("phone_number")
    @classmethod
    def check_phone_number(cls, v: str) -> str:
        try:
            validate_international_phonenumber(v)
            return v
        except ValidationError as e:
            error = e.message if hasattr(e, 'message') else e.messages[0]
            raise ValueError(error)
        
class RefreshTokenRequestMSG(msgspec.Struct):
    refresh: str | None = None
    
class RefreshTokenRequest(Schema):
    refresh: str | None = None

class SimpleTrackSchema(Schema):
    id: PositiveInt
    name: str

class TrackCreateMSG(Serializer):
    name: str
    prefix: str
    en_description: str
    ar_description: str

class TrackCreateSchema(Schema):
    name: str
    prefix: str
    en_description: str
    ar_description: str

class TrackSchema(Schema):
    id: PositiveInt
    name: str
    en_description: str
    ar_description: str
    image: str

class RegisterResponseMSG(msgspec.Struct):
    code: str
    track: TrackNameOnlyMSGSerializer
    email: str
    name: str

class RegisterResponse(Schema):
    code: str
    track: SimpleTrackSchema
    email: str
    name: str
    
class TestAuthResponseMSG(msgspec.Struct):    
    username: str
    role: models.UserRole
    is_admin: bool
    settings: SiteSettingsImagesMSGSerializer
    track: TrackNameOnlyMSGSerializer | None = None
    
class TestAuthResponse(Schema):    
    username: str
    role: models.UserRole
    is_admin: bool
    track: SimpleTrackSchema | None
    settings: SettingsImagesResponse
