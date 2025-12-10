from . import models
from core.models import Track
from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin

# Register your models here.


@admin.register(models.Attendance)
class AttendanceAdmin(UnfoldModelAdmin):
    list_display = ("id", "member", "get_member_track", "date", "status")
    list_display_links = ("id", "member")
    search_fields = ("member__name", "member__code")
    
    def get_member_track(self, obj: models.Attendance) -> Track:
        return obj.member.track

    get_member_track.short_description = "Track" # type: ignore
    