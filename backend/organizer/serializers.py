from core.serializers import TrackNoDescSerializer
from rest_framework import serializers
from . import models

class AttendanceSmallDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AttendanceAllowedDay
        fields = ('id', "day")
    

class AttendanceDaysSerializer(serializers.ModelSerializer):
    track = TrackNoDescSerializer(read_only=True)
    class Meta:
        model = models.AttendanceAllowedDay
        fields = ('id', "day", "track")
    

class AttendenceSmallSerializer(serializers.ModelSerializer):
    date = AttendanceSmallDaysSerializer()
    class Meta:
        model = models.Attendance
        fields = ("date", "status", "excuse_reason")
        

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SiteSetting
        fields = '__all__'
    
        
