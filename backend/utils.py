from phonenumber_field.phonenumber import PhoneNumber
from rest_framework.exceptions import ErrorDetail
import msgspec

def enc_phone_str(obj) -> str:
    if isinstance(obj, PhoneNumber):
        return obj.as_e164
    elif isinstance(obj, ErrorDetail):
        return str(obj)
    
    raise TypeError(f"Object of Type {type(obj)} is not a json serializer")

def dec_str_phone(t, obj) -> PhoneNumber:
    if t is PhoneNumber and isinstance(obj, str):
        return PhoneNumber.from_string(obj)
    raise TypeError(f"Object of Type {type(obj)} is not a json serializer")


serializer_encoder = msgspec.json.Encoder(enc_hook=enc_phone_str)

DEFAULT_CACHE_DURATION = 3600
"1 hour in seconds"

SAFE_MIMETYPES = ('application/pdf', 'image/jpeg', 'image/png', 'image/webp')
