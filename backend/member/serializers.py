from technical.serializers import TaskSerializer, TrackSerializer
from rest_framework import serializers
from . import models

class MemberSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    class Meta:
        model = models.Member
        fields = '__all__'

class RecivedTaskSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    member = MemberSerializer(read_only=True)
    
    class Meta:
        model = models.ReciviedTask
        fields = '__all__'


