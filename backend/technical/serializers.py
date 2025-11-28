from rest_framework import serializers
from . import models

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Track
        fields = ("id", "track")

class TaskSerializer(serializers.ModelSerializer):
    track = TrackSerializer()
    
    class Meta:
        model = models.Task
        fields = '__all__'




