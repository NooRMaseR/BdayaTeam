from technical.api_schemas import TaskNoTrackSerializer, TaskSmallSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from organizer.api_schemas import AttendenceSmallSerializer
from core.api_schemas import TrackNameOnlySerializer
from rest_framework import serializers
from . import models

class MemberSerializer(serializers.ModelSerializer):
    track = TrackNameOnlySerializer(read_only=True)
    attendances = AttendenceSmallSerializer(read_only=True, many=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    phone_number = PhoneNumberField(read_only=True, region="EG")
    
    class Meta:
        model = models.Member
        exclude = ('joined_at',)
        

class RecivedTaskSmallSerializer(serializers.ModelSerializer):
    member_code = serializers.CharField(read_only=True)
    task = TaskSmallSerializer(read_only=True)
    
    class Meta:
        model = models.ReciviedTask
        fields = (
            "id",
            "task",
            "member_code",
            "technical_notes",
            "degree"
        )

class MemberTechnicalSerializer(serializers.ModelSerializer):
    tasks = RecivedTaskSmallSerializer(read_only=True, many=True)
    track = TrackNameOnlySerializer(read_only=True)
    email = serializers.EmailField(read_only=True)
    name = serializers.CharField(read_only=True)
    phone_number = PhoneNumberField(read_only=True)
    
    class Meta:
        model = models.Member
        exclude = ('joined_at',)

class MemberSerializerForTask(serializers.ModelSerializer):
    class Meta:
        model = models.Member
        fields = ('code', 'name')

class RecivedTaskFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReciviedTaskFile
        fields = ("id", "file", "file_name")

class RecivedTaskSerializer(serializers.ModelSerializer):
    task = TaskNoTrackSerializer(read_only=True)
    member = MemberSerializerForTask(read_only=True)
    
    files = serializers.ListField(
        child=serializers.FileField(),
        required=False,
        write_only=True
    )

    files_url = RecivedTaskFileSerializer(many=True)
    
    class Meta:
        model = models.ReciviedTask
        fields = '__all__'
        
    def create(self, validated_data):
        files = validated_data.pop("files")
        recive_task = models.ReciviedTask.objects.create(**validated_data)
        oc_files = (models.ReciviedTaskFile(task=recive_task, file=f) for f in files)
        
        models.ReciviedTaskFile.objects.bulk_create(oc_files)
        return recive_task


class MemberProfileSerializer(serializers.ModelSerializer):
    absents = serializers.IntegerField(read_only=True)
    track = TrackNameOnlySerializer(read_only=True)
    total_tasks_sent = serializers.IntegerField()
    missing_tasks = serializers.IntegerField()
    tasks = RecivedTaskSerializer(read_only=True, many=True)
    
    class Meta:
        model = models.Member
        fields = (
            "name",
            "code",
            "track",
            "status",
            "absents",
            "total_tasks_sent",
            "missing_tasks",
            "tasks"
        )