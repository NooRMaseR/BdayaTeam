import msgspec

class TrackNameOnlyMSGSerializer(msgspec.Struct):
    id: int
    track: str

class TrackMSGSerializer(msgspec.Struct):
    id: int
    track: str
    description: str
    image: str