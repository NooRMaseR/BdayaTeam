from core.serializers import TrackSerializer
from rest_framework import serializers
from . import models


class TaskSerializer(serializers.ModelSerializer):
    track_id = serializers.PrimaryKeyRelatedField(
        source="track",
        queryset=models.Track.objects.all(),
        write_only=True
    )
    track = TrackSerializer(read_only=True)
    expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = models.Task
        fields = '__all__'





