from rest_framework import serializers
from django.db import IntegrityError
from member.models import Member
from . import models

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Track
        fields = '__all__'
        extra_kwargs = {"prefix": {"write_only": True}}

class TrackNameOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Track
        fields = ("id", "track")

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    role = serializers.ChoiceField(models.UserRole)
    track = TrackNameOnlySerializer(allow_null=True)


class RegisterMemberSerializer(serializers.ModelSerializer):
    request_track_id = serializers.PrimaryKeyRelatedField(
        source="track",
        queryset=models.Track.objects.all(),
        write_only=True
    )
    track = TrackNameOnlySerializer(read_only=True)
    class Meta:
        model = Member
        exclude = ("bonus", "joined_at", "status")
        extra_kwargs = {
            "code": {"read_only": True},
            "email": {"write_only": True},
            "collage_code": {"write_only": True},
            "phone_number": {"write_only": True},
        }
        
    def create(self, validated_data):
        track: models.Track = validated_data["track"]
        prefix = track.prefix
        
        counter, _ = models.TrackCounter.objects.select_for_update().get_or_create(track=track)
        counter.current_value += 1
        counter.save()
        
        validated_data["code"] = f"{prefix}-{counter.current_value}"
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            raise serializers.ValidationError({"details": "something went wrong, Please try again.", "error": repr(e)})
    
class ForbiddenOnlyTechnical(serializers.Serializer):
    details = serializers.CharField(default="Only technicals Allowed")
    
class ForbiddenOnlyMember(serializers.Serializer):
    details = serializers.CharField(default="Only members Allowed")
    
class ForbiddenOnlyOrganizer(serializers.Serializer):
    details = serializers.CharField(default="Only organizers Allowed")