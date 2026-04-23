from phonenumber_field.phonenumber import PhoneNumber
from django_bolt.auth import DjangoCacheRevocation
from django_bolt.param_functions import Form
from django_bolt import create_jwt_for_user
from core.models import BdayaUser
from django.conf import settings
from typing import Annotated
from enum import Enum
from PIL import Image
import msgspec
import uuid
import time
import io

class GeneratedJWT(msgspec.Struct):
    access: str
    refresh: str
    access_exp: int
    refresh_exp: int

def generate_jwts_for_user(user: BdayaUser) -> GeneratedJWT:
    ACCESS_EXP = int(settings.BOLT_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds())
    REFRESH_EXP = int(settings.BOLT_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds())
    current_time = int(time.time())
    
    claims = {
        "role": user.role
    }
    if user.is_member and hasattr(user, "member"):
        claims['code'] = user.member.code # type: ignore
    
    access_token = create_jwt_for_user(
        user, 
        extra_claims={
            **claims,
            "token_type": "access",
            "exp": current_time + ACCESS_EXP,
            "sub": str(user.pk),
            "jti": str(uuid.uuid4())
        }
    )
    refresh_token = create_jwt_for_user(
        user, 
        extra_claims={
            **claims,
            "token_type": "refresh",
            "exp": current_time + REFRESH_EXP,
            "sub": str(user.pk),
            "jti": str(uuid.uuid4())
        }
    )
    
    return GeneratedJWT(
        access= access_token, 
        refresh= refresh_token,
        access_exp= ACCESS_EXP,
        refresh_exp= REFRESH_EXP,
    )

def generate_dummy_image() -> bytes:
    file_obj = io.BytesIO()
    image = Image.new("RGB", size=(1, 1), color=(255, 0, 0))
    image.save(file_obj, "jpeg")
    file_obj.seek(0)
    return file_obj.read()

def _enc_str(obj) -> str:
    if isinstance(obj, PhoneNumber):
        return obj.as_e164
    elif isinstance(obj, Enum):
        return str(obj)
    
    raise TypeError(f"Object of Type {type(obj)} is not a json serializer")

serializer_encoder = msgspec.json.Encoder(enc_hook=_enc_str)

STORE = DjangoCacheRevocation()

DEFAULT_CACHE_DURATION = 3600
"1 hour in seconds"
JSON_CONTENT_TYPE = "application/json"
SAFE_MIMETYPES = ('application/pdf', 'image/jpeg', 'image/png', 'image/webp', 'video/mp4', 'video/wav', 'video/wave')

IntId = Annotated[int, msgspec.Meta(gt=0)]
"Represents an integer > 0"

FormStr = Annotated[str, Form()]
