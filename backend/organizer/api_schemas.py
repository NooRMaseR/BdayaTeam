from rest_framework import serializers
from . import models

class AttendanceSmallDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AttendanceAllowedDay
        fields = ('id', "day")
    

class AttendanceDaysSerializer(serializers.ModelSerializer):
    # track = TrackNameOnlySerializer(read_only=True)
    class Meta:
        model = models.AttendanceAllowedDay
        fields = ('id', "day")
    

class AttendenceSmallSerializer(serializers.ModelSerializer):
    date = AttendanceSmallDaysSerializer()
    class Meta:
        model = models.Attendance
        fields = ("date", "status", "excuse_reason")
        

class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SiteSetting
        fields = '__all__'
        

class SiteSettingsImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SiteSetting
        fields = ("site_image", "hero_image")
    
        
