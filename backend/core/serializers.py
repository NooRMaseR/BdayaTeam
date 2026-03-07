from abc import abstractmethod, ABCMeta
from collections.abc import Iterable
from utils import serializer_encoder
from typing import Any, Self
from .models import Track
import msgspec

class CombinedMetaClass(msgspec.StructMeta, ABCMeta): ...

class BaseMSGSerializer[T](msgspec.Struct, frozen=True, metaclass=CombinedMetaClass):
    "Base Serializer for `Struct` for ease of use, must override the `from_model`"
    
    @classmethod
    @abstractmethod
    def from_model(cls, model: T) -> Self:
        "Converts a `django.db.models.Model` into a `Struct`"
        ...
    
    @classmethod
    def from_model_values(cls, model: dict[str, Any]) -> Self:
        "Converts a `Model` converted using `.values()` into a `Struct`"
        return msgspec.convert(model, cls)
        
    @classmethod
    def from_queryset_values(cls, models: Iterable[dict[str, Any]]) -> list[Self]:
        "Converts a `QuerySet` or `list` of models to a `Struct`"
        return [cls.from_model_values(t) for t in models]
    
    @classmethod
    def from_queryset(cls, models: Iterable[T]) -> list[Self]:
        "Converts a `QuerySet` or `list` of models to a `Struct`"
        return [cls.from_model(t) for t in models]
        
    def encode(self) -> bytes:
        return serializer_encoder.encode(self)
    
        
class TrackNameOnlyMSGSerializer(BaseMSGSerializer[Track], frozen=True):
    id: int
    name: str

    @classmethod
    def from_model(cls, model: Track) -> Self:
        return cls(
            id=model.pk,
            name=model.name
        )


class TrackMSGSerializer(BaseMSGSerializer[Track], frozen=True):
    id: int
    name: str
    en_description: str
    ar_description: str
    image: str

    @classmethod
    def from_model(cls, model: Track):
        return cls(
            id=model.pk,
            name=model.name,
            en_description=model.en_description,
            ar_description=model.ar_description,
            image=model.image.url
        )
