from technical.serializers import TaskSerializer, TrackSerializer
from rest_framework import serializers
from . import models

class MemberSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    class Meta:
        model = models.Member
        fields = '__all__'

class RecivedTaskFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReciviedTaskFile
        fields = ("id", "file")

class RecivedTaskSerializer(serializers.ModelSerializer):
    track = TrackSerializer(read_only=True)
    task = TaskSerializer(read_only=True)
    member = MemberSerializer(read_only=True)
    
    # 1. WRITE ONLY: Used for uploading files
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True  # Hides this field from the output to prevent the crash
    )

    # 2. READ ONLY: Used for displaying file URLs in the response
    files_url = serializers.SerializerMethodField()
    
    class Meta:
        model = models.ReciviedTask
        fields = '__all__'
        
    def get_files_url(self, obj) -> list[str]:
        return [f.file.url for f in obj.files.all() if f.file]
        
    def create(self, validated_data):
        files = validated_data.pop("files")
        recive_task = models.ReciviedTask.objects.create(**validated_data)
        oc_files = (models.ReciviedTaskFile(task=recive_task, file=f) for f in files)
        
        models.ReciviedTaskFile.objects.bulk_create(oc_files)
        return recive_task


