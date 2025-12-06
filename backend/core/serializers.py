from rest_framework import serializers
from django.db import transaction
from member.models import Member
from . import models

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Track
        exclude = ("prefix",)

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = serializers.ChoiceField(models.UserRole)
    token = serializers.CharField()
    track = TrackSerializer(allow_null=True)


class RegisterSerializer(serializers.ModelSerializer):
    request_track_id = serializers.PrimaryKeyRelatedField(
        source="track",
        queryset=models.Track.objects.all(),
        write_only=True
    )
    track = TrackSerializer(read_only=True)
    class Meta:
        model = Member
        fields = '__all__'
        extra_kwargs = {
            "code": {"read_only": True},
            "bonus": {"read_only": True}
        }
        
    def create(self, validated_data):
        track: models.Track = validated_data["track"]
        prefix = track.prefix
        
        with transaction.atomic():
            last_member = Member.objects.only("id", "code").filter(track=track).order_by("-code").first()
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