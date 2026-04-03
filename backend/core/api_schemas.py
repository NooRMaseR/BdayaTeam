from phonenumber_field.validators import validate_international_phonenumber
from organizer.api_schemas import SettingsImagesResponse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from pydantic import EmailStr, field_validator
from . import models, validators
from ninja import Schema

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

class LoginResponse(Schema):
    username: str
    is_admin: bool
    role: models.UserRole
    track: SimpleTrackSchema | None = None

class ErrorResponse(Schema):
    details: str

class SingleErrorResponse(Schema):
    detail: str
    
class RegisterRequest(Schema):
    request_track_id: int
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
        
class RefreshTokenRequest(Schema):
    refresh: str | None = None

class SimpleTrackSchema(Schema):
    id: int
    name: str

class TrackCreateSchema(Schema):
    name: str
    prefix: str
    en_description: str
    ar_description: str

class TrackSchema(Schema):
    id: int
    name: str
    en_description: str
    ar_description: str
    image: str

class RegisterResponse(Schema):
    code: str
    track: SimpleTrackSchema
    email: str
    name: str
    
class TestAuthResponse(Schema):
    username: str
    role: models.UserRole
    is_admin: bool
    track: SimpleTrackSchema | None
    settings: SettingsImagesResponse
    