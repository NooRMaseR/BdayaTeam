from django_bolt.auth import DjangoCacheRevocation, create_token_pair
from imagekit.models.fields.files import ProcessedImageFieldFile
from phonenumber_field.phonenumber import PhoneNumber
from django.http import HttpResponse
from core.models import BdayaUser
from django.conf import settings
from typing import Any, Literal
from compression import zstd
from enum import Enum
from PIL import Image
import msgspec
import time
import io

type SupportedEncodings = Literal["zstd", "br", "gzip"]

class GeneratedJWT(msgspec.Struct):
    access: str
    refresh: str
    access_exp: int
    refresh_exp: int

def generate_jwts_for_user(user: BdayaUser) -> GeneratedJWT:
    current_time = int(time.time())
    ACCESS_EXP = int(settings.BOLT_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()) + current_time
    REFRESH_EXP = int(settings.BOLT_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()) + current_time
    
    claims = {
        "role": user.role,
        "username": user.username
    }
    if user.is_member and hasattr(user, "member"):
        claims['code'] = user.member.code # type: ignore
    
    tokens = create_token_pair(
        user, 
        claims=claims, 
        access_ttl=ACCESS_EXP,
        refresh_ttl=REFRESH_EXP,
    )
    
    return GeneratedJWT(
        access= tokens.access_token, 
        refresh= tokens.refresh_token,
        access_exp= ACCESS_EXP,
        refresh_exp= REFRESH_EXP,
    )

def generate_dummy_image() -> bytes:
    file_obj = io.BytesIO()
    image = Image.new("RGB", size=(1, 1), color=(255, 0, 0))
    image.save(file_obj, "jpeg")
    file_obj.seek(0)
    return file_obj.read()

def encode_compress(data: Any, compress_level: int = 4) -> bytes:
    """a wrapper function to encode the data using `serializer_encoder` (`msgspec.json.Encoder`) and compressing the data using `compression.zstd`

    Args:
        data (Any): the data to process (encode then compress)
        compress_level (int, optional): the compression level. Defaults to 4.

    Returns:
        bytes: the compressed version of the data
    """
    encoded_data = serializer_encoder.encode(data)
    return zstd.compress(encoded_data, compress_level)

def wrap_compressed_http_response(body: bytes, encoding: SupportedEncodings = 'zstd') -> HttpResponse:
    """a temporary wrapper for creating an `HttpResponse` with prober `Content-Encoding` header

    Args:
        body (bytes): the body to send
        encoding (SupportedEncodings, optional): the encoding to add to the header. Defaults to 'zstd'.

    Returns:
        HttpResponse: the final response
    """
    response =  HttpResponse(body, content_type=JSON_CONTENT_TYPE)
    response['Content-Encoding'] = encoding
    return response

def _enc_hook(obj) -> str:
    if isinstance(obj, PhoneNumber):
        return obj.as_e164
    elif isinstance(obj, Enum):
        return str(obj)
    elif isinstance(obj, ProcessedImageFieldFile):
        return obj.url
    
    raise TypeError(f"Object of Type {type(obj)} is not a json serializer")

serializer_encoder = msgspec.json.Encoder(enc_hook=_enc_hook)

STORE = DjangoCacheRevocation()

DEFAULT_CACHE_DURATION = 3600
"1 hour in seconds"
JSON_CONTENT_TYPE = "application/json"
SAFE_MIMETYPES = ('application/pdf', 'image/jpeg', 'image/png', 'image/webp', 'video/mp4', 'video/wav', 'video/wave')

