from django_bolt.serializers import Serializer, field_validator
from collections.abc import AsyncIterable, Iterable
from django.db.models.manager import BaseManager
from utils import serializer_encoder
from typing import Any, Self
import msgspec

class ExtraSerialization:
    
    @classmethod
    def from_values(cls, model: dict[str, Any]) -> Self:
        return msgspec.convert(model, cls)

    @classmethod
    def from_queryset_values(cls, models: Iterable[dict[str, Any]]) -> list[Self]:
        return msgspec.convert(models, list[cls])

    @classmethod
    async def afrom_queryset_values(cls, models: AsyncIterable[dict[str, Any]] | BaseManager) -> list[Self]:
        evaluated_list = [row async for row in models]
        return msgspec.convert(evaluated_list, list[cls])
        
    def encode(self) -> bytes:
        return serializer_encoder.encode(self)
    
        
class TrackNameOnlyMSGSerializer(Serializer, ExtraSerialization):
    id: int
    name: str

class TrackMSGSerializer(TrackNameOnlyMSGSerializer):
    en_description: str
    ar_description: str
    image: str
    
    @field_validator('image', 'before')
    @classmethod
    def transform_image(cls, v):
        return v.url
