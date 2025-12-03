from typing import Any
from django.db.models import Model
from django.forms import Form
from django.http import HttpRequest
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from unfold.contrib.filters.admin.choice_filters import ChoicesCheckboxFilter
from django.contrib.auth.models import Group
from django.contrib import admin
from . import models

# Register your models here.

admin.site.unregister(Group)

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, UnfoldModelAdmin):
    pass


@admin.register(models.BdayaUser)
class BdayaUserAdmin(UnfoldModelAdmin):
    list_display = ("id", "username", "email", "phone_number", "role", "is_active", "is_staff", "is_superuser", "joined_at")
    search_fields = ("username", "email", "phone_number")
    list_filter = (
        ("role", ChoicesCheckboxFilter),
    )
    list_filter_submit = True
    
    def save_model(self, request: HttpRequest, obj: Model, form: Form, change: Any) -> None:
        if "password" in form.changed_data:
            obj.set_password(form.cleaned_data.get("password")) # type: ignore
        
        return super().save_model(request, obj, form, change)


@admin.register(models.Attendance)
class AttendanceAdmin(UnfoldModelAdmin):
    list_display = ("id", "member", "get_member_track", "date")
    search_fields = ("member__name", "member__code")
    
    def get_member_track(self, obj: models.Attendance) -> models.Track:
        return obj.member.track

    get_member_track.short_description = "Track" # type: ignore
    