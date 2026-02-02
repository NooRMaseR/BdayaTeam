from unfold.contrib.filters.admin.choice_filters import ChoicesCheckboxFilter
from unfold.admin import ModelAdmin as UnfoldModelAdmin, StackedInline
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from unfold.paginator import InfinitePaginator
from django.contrib.auth.models import Group
from django.http import HttpRequest
from django.db.models import Model
from django.contrib import admin
from django.forms import Form
from typing import Any
from . import models

# Register your models here.

admin.site.unregister(Group)

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, UnfoldModelAdmin):
    pass


@admin.register(models.BdayaUser)
class BdayaUserAdmin(UnfoldModelAdmin):
    list_display = ("id", "username", "email", "phone_number", "role", "is_active", "is_staff", "is_superuser", "joined_at")
    list_display_links = ("id", "username", "email")
    search_fields = ("username", "email", "phone_number")
    list_filter = (
        ("role", ChoicesCheckboxFilter),
    )
    list_filter_submit = True
    paginator = InfinitePaginator
    list_per_page = 50
    
    def save_model(self, request: HttpRequest, obj: Model, form: Form, change: Any) -> None:
        if "password" in form.changed_data:
            obj.set_password(form.cleaned_data.get("password")) # type: ignore
        
        return super().save_model(request, obj, form, change)


class TrackTechnichal(StackedInline):
    model = models.BdayaUser
    fields = ("username", "email", "phone_number")
    extra = 0
    tab=True
    collapsible=True
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=models.UserRole.TECHNICAL)


@admin.register(models.Track)
class CourseAdmin(UnfoldModelAdmin):
    list_display = ("id", "image", "track", "prefix")
    list_display_links = ("id", "track")
    search_fields = ("track", )
    inlines = [TrackTechnichal]
    paginator = InfinitePaginator
    list_per_page = 50

@admin.register(models.TrackCounter)
class TrackCounterAdmin(UnfoldModelAdmin):
    list_display = ("id", "track", "current_value")
    list_display_links = ("id", "track")
    search_fields = ("track", )
    paginator = InfinitePaginator
    list_per_page = 50