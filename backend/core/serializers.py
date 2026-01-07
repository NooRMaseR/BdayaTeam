from rest_framework import serializers
from django.db import transaction
from member.models import Member
from . import models

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Track
        fields = '__all__'
        extra_kwargs = {"prefix": {"write_only": True}}

class TrackNoDescSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Track
        exclude = ("prefix", "description")

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = serializers.ChoiceField(models.UserRole)
    track = TrackNoDescSerializer(allow_null=True)


class RegisterSerializer(serializers.ModelSerializer):
    request_track_id = serializers.PrimaryKeyRelatedField(
        source="track",
        queryset=models.Track.objects.all(),
        write_only=True
    )
    track = TrackNoDescSerializer(read_only=True)
    class Meta:
        model = Member
        exclude = ("bonus",)
        extra_kwargs = {
            "code": {"read_only": True},
        }
        
    def create(self, validated_data):
        track: models.Track = validated_data["track"]
        prefix = track.prefix
        
        with transaction.atomic():
            last_member = Member.objects.only("code").filter(track=track).order_by("-joined_at").first()
            if last_member:
                last_id = int(last_member.code.split("-")[1]) + 1
            else:
                last_id = 1
            
            validated_data["code"] = f"{prefix}-{last_id}"
            return super().create(validated_data)
    
class ForbiddenOnlyTechnical(serializers.Serializer):
    details = serializers.CharField(default="Only technicals Allowed")
    
class ForbiddenOnlyMember(serializers.Serializer):
    details = serializers.CharField(default="Only members Allowed")
    
class ForbiddenOnlyOrganizer(serializers.Serializer):
    details = serializers.CharField(default="Only organizers Allowed")