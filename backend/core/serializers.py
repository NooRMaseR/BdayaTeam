from rest_framework import serializers
from core.models import BdayaUser
from member.models import Member
from . import models

class LoginSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    role = serializers.ChoiceField(models.UserRole)
    token = serializers.CharField()
    

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
        extra_kwargs = {
            "code": {"read_only": True}
        }
        
    def create(self, validated_data):
        track: models.Track = validated_data["track"]
        prefix = track.prefix
        
        last_id = Member.objects.filter(track=track).order_by("-code").first()
        if last_id:
            last_id = int(last_id.code.split("-")[1]) + 1
        else:
            last_id = 1
        
        validated_data["code"] = f"{prefix}-{last_id}"
        return super().create(validated_data)
    