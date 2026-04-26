from django.core.exceptions import ValidationError
from collections.abc import Iterable
from django_bolt import UploadFile
from .models import Track
import filetype
import asyncio
import uuid
import os
import re

STUDENT_CODE_PATTERN = re.compile(r"^\w-\d+$")
COLLAGE_CODE_PATTERN = re.compile(r"^[MCAE]\d+$")

def validate_member_code(code: str) -> None:
    """validate member's code

    Args:
        code (str): the member code

    Raises:
        ValidationError: if code is not valid
    """
    
    if not re.match(STUDENT_CODE_PATTERN, code):
        raise ValidationError("code must start with the specified prefix")

def validate_collage_code(code: str) -> None:
    """validate member collage code

    Args:
        code (str): the collage code to validate

    Raises:
        ValidationError: if the code is not uppercased
        ValidationError: if the code is not valid
    """
    
    if not code.isupper():
        raise ValidationError("Code Must Start With an Upper case Litter")
    
    if not re.match(COLLAGE_CODE_PATTERN, code):
        raise ValidationError("collage Code is Not Valid")

async def _validate_track_file(uploaded_file: UploadFile, track: Track, extensions: Iterable[str]) -> UploadFile:
    ext = os.path.splitext(uploaded_file.filename)[1][1:].lower()
    if ext == "jpeg":
        ext = "jpg"
    
    if ext not in extensions:
        raise ValueError(f"Extension '{ext}' is not allowed for {track.name}.")

    chunk = await uploaded_file.read(2048)
    await uploaded_file.seek(0)
    
    kind = filetype.guess(chunk)

    if kind is not None:
        detected_ext = kind.extension.lower()
        if detected_ext == "jpeg":
            detected_ext = "jpg"

        if detected_ext != ext:
            raise ValueError(f"Security Error: File claims to be {ext} but is actually {detected_ext}")
        
    else:
        # if the filetype doesn't know what it is then test if it's plain text
        try:
            chunk.decode('utf-8')
        except UnicodeDecodeError:
            raise ValueError(f"Security Error: File claims to be '{ext}' but contains hidden binary malware")

    safe_filename = f"{uuid.uuid4().hex}.{ext}"
    uploaded_file.filename = safe_filename

    return uploaded_file

async def validate_track_task_files(uploaded_files: Iterable[UploadFile], track: Track) -> list[UploadFile]:
    """Validates a file against the track's allowed extensions and magic numbers

    Args:
        uploaded_files (Iterable[UploadFile]): the uploaded files to process
        track (Track): the track instance itself

    Raises:
        ValueError: if rules aren't set for this track
        ValueError: if the extension is not supported
        ValueError: if unknown file extension
        ValueError: if the file claims to be somthing else

    Returns:
        list[UploadFile]: the validated files
    """
    
    if not uploaded_files:
        return []

    from member.models import AllowedTrackFileExtention
    

    try:
        rules = await AllowedTrackFileExtention.objects.only("extensions").aget(track=track)
    except AllowedTrackFileExtention.DoesNotExist:
        raise ValueError(f"No upload rules defined for track: {track.name}")
    
    return await asyncio.gather(
        *[
            _validate_track_file(file, track, rules.extensions)
            for file in uploaded_files
        ]
    )
