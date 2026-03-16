from phonenumber_field.validators import validate_international_phonenumber
from django.utils.translation import gettext_lazy as _
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.db import IntegrityError
from member.models import Member
from . import models, validators

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Track
        fields = '__all__'
        extra_kwargs = {"prefix": {"write_only": True}}

class TrackNameOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Track
        fields = ("id", "name")

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    is_admin = serializers.BooleanField(default=False)
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
            "email": {
                "write_only": True,
                "validators": [
                    UniqueValidator(
                        queryset=Member.objects.all(),
                        message=_("email_exists"),
                    )
                ]
            },
            "collage_code": {
                "write_only": True,
                "error_messages": {
                    "unique": _("collage_code_exists")
                },
                "validators": [
                    validators.validate_collage_code,
                    UniqueValidator(
                        queryset=Member.objects.all(),
                        message=_("collage_code_exists")
                    )
                ]
            },
            "phone_number": {
                "write_only": True,
                "error_messages": {
                    "invalid": _("phone_not_valid")
                },
                "validators": [
                    validate_international_phonenumber,
                    UniqueValidator(
                        queryset=Member.objects.all(),
                        message=_("phone_exists")
                    )
                ]
            }
        }
        
    def create(self, validated_data):
        track: models.Track = validated_data["track"]
        prefix = track.prefix
        
        counter, _ = models.TrackCounter.objects.select_for_update().get_or_create(track=track)
        counter.current_value += 1
        counter.save()
        
        try:
            validated_data["code"] = f"{prefix}-{counter.current_value}"
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({"details": "something went wrong, Please try again."})
    
class ForbiddenOnlyTechnical(serializers.Serializer):
    details = serializers.CharField(default="Only technicals Allowed")
    
class ForbiddenOnlyMember(serializers.Serializer):
    details = serializers.CharField(default="Only members Allowed")
    
class ForbiddenOnlyOrganizer(serializers.Serializer):
    details = serializers.CharField(default="Only organizers Allowed")