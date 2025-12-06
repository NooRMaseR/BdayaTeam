from rest_framework import serializers
from . import models

class AttendenceSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Attendance
        fields = ("date", "status", "excuse_reason")
        
