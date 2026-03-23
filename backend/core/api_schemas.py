from phonenumber_field.serializerfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _
from rest_framework.validators import UniqueValidator
from django.db import IntegrityError, transaction
from rest_framework import serializers
from .tasks import send_member_email
from member.models import Member
from . import models, validators
from typing import Any


class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Track
        fields = "__all__"
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
        source="track", queryset=models.Track.objects.all(), write_only=True
    )
    track = TrackNameOnlySerializer(read_only=True)

    email = serializers.EmailField(
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=models.BdayaUser.objects.all(), message=_("email_exists")
            )
        ],
    )
    name = serializers.CharField(write_only=True)
    phone_number = PhoneNumberField(
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=models.BdayaUser.objects.all(), message=_("phone_exists")
            )
        ],
    )

    class Meta:
        model = Member
        exclude = ("bonus", "joined_at", "status", "bdaya_user")
        extra_kwargs = {
            "code": {"read_only": True},
            "collage_code": {
                "write_only": True,
                "error_messages": {"unique": _("collage_code_exists")},
                "validators": [
                    validators.validate_collage_code,
                    UniqueValidator(
                        queryset=Member.objects.all(), message=_("collage_code_exists")
                    ),
                ],
            },
        }

    def create(self, validated_data: dict[str, Any]) -> Member:
        email = validated_data.pop("email")
        username = validated_data.pop("name")
        phone_number = validated_data.pop("phone_number")

        track: models.Track = validated_data["track"]
        prefix = track.prefix

        counter, _ = models.TrackCounter.objects.select_for_update().get_or_create(
            track=track
        )
        counter.current_value += 1
        counter.save()
        code = f"{prefix}-{counter.current_value}"
        collage_code = validated_data.pop("collage_code")

        try:
            GENERATED_PASSWORD = f"{code}@{collage_code}"

            user = models.BdayaUser(
                email=email,
                username=username,
                phone_number=phone_number,
                track=track,
                role=models.UserRole.MEMBER,
            )
            user.set_password(GENERATED_PASSWORD)
            user.save()
            
            member = Member.objects.create(
                bdaya_user=user, code=code, collage_code=collage_code, track=track
            )

            transaction.on_commit(
                lambda: send_member_email(
                    user.username,
                    user.email,
                    GENERATED_PASSWORD,
                    member.code,
                    member.track.name,
                )
            )

            return member
        except IntegrityError:
            raise serializers.ValidationError(
                {"details": "something went wrong, Please try again."}
            )


class ForbiddenOnlyTechnical(serializers.Serializer):
    details = serializers.CharField(default="Only technicals Allowed")


class ForbiddenOnlyMember(serializers.Serializer):
    details = serializers.CharField(default="Only members Allowed")


class ForbiddenOnlyOrganizer(serializers.Serializer):
    details = serializers.CharField(default="Only organizers Allowed")
