from . import models
from typing import Any
from core.models import Track
from django.contrib import admin
from django.http import HttpRequest
from django.forms.models import ModelForm
from solo.admin import SingletonModelAdmin
from unfold.contrib.forms.widgets import ArrayWidget
from django.contrib.postgres.fields import ArrayField
from unfold.admin import ModelAdmin as UnfoldModelAdmin

# Register your models here.
@admin.register(models.SiteSetting)
class Site(SingletonModelAdmin, UnfoldModelAdmin):
    formfields_overrides = {
        ArrayField: {
            "widget": ArrayWidget
        }
    }
    
    def get_form(self, request: HttpRequest, obj: Any | None = None, change: bool = False, **kwargs: Any) -> type[ModelForm]:
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields['organizer_can_edit'].widget = ArrayWidget() # type: ignore
        return form

@admin.register(models.Attendance)
class AttendanceAdmin(UnfoldModelAdmin):
    list_display = ("id", "member", "get_member_track", "status")
    list_display_links = ("id", "member")
    search_fields = ("member__name", "member__code")
    
    def get_member_track(self, obj: models.Attendance) -> Track:
        return obj.member.track

    get_member_track.short_description = "Track" # type: ignore


@admin.register(models.AttendanceAllowedDay)
class AttendanceDayAdmin(UnfoldModelAdmin):
    list_display = ("id", "day", "track__track")
    list_display_links = ("id", "day")
    search_fields = ("day", )
    