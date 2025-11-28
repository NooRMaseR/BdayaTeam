from django.core.exceptions import ValidationError
import re


STUDENT_CODE_VALID = re.compile(r"^\w-\d+$")
COLLAGE_CODE_VALID = re.compile(r"^[MCA]\d{7}$", re.IGNORECASE)

def validate_student_code(code: str) -> None:
    if not re.match(STUDENT_CODE_VALID, code):
        raise ValidationError("code must start with the specified prefix")

def validate_collage_code(code: str) -> None:
    if not re.match(COLLAGE_CODE_VALID, code):
        raise ValidationError("collage Code is Not Valid")
