from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers
from . import models

@extend_schema_serializer(exclude_fields=('track',))
class TaskSerializer(serializers.ModelSerializer):
    track = serializers.PrimaryKeyRelatedField(read_only=True)
    expired = serializers.BooleanField(read_only=True)
    
    def validate(self, attrs):
        track = self.context.get('track')
        task_number = attrs.get('task_number')
        
        if models.Task.objects.filter(track=track, task_number=task_number).exists():
            raise serializers.ValidationError({
                "task_number": "This task number already exists"
            })
        return super().validate(attrs)
    
    class Meta:
        model = models.Task
        fields = '__all__'

class TaskNoTrackSerializer(serializers.ModelSerializer):
    expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = models.Task
        fields = '__all__'





