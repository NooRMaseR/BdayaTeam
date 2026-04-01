from typing import Any, Literal, TypedDict
from rest_framework import serializers
from . import models

class AttendanceSmallDaysSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AttendanceAllowedDay
        fields = ('id', "day")
    

class AttendanceDaysSerializer(serializers.ModelSerializer):
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
   
class OrganizerBroudCastData(TypedDict):
    code: str
    changedKey: str
    changedValue: Any
    
class OrganizerBroudCast(TypedDict):
    type: Literal["edit"]
    data: OrganizerBroudCastData
