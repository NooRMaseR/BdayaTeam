from django.core.exceptions import ValidationError
import re

STUDENT_CODE_PATTERN = re.compile(r"^\w-\d+$")
COLLAGE_CODE_PATTERN = re.compile(r"^[MCAE]\d+$")

def validate_member_code(code: str) -> None:
    if not re.match(STUDENT_CODE_PATTERN, code):
        raise ValidationError("code must start with the specified prefix")

def validate_collage_code(code: str) -> None:
    if not code.isupper():
        raise ValidationError("Code Must Start With an Upper case Litter")
    
    if not re.match(COLLAGE_CODE_PATTERN, code):
        raise ValidationError("collage Code is Not Valid")
