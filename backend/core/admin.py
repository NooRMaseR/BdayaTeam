from unfold.contrib.filters.admin.choice_filters import ChoicesCheckboxFilter
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
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
    search_fields = ("username", "email", "phone_number")
    list_filter = (
        ("role", ChoicesCheckboxFilter),
    )
    list_filter_submit = True
    
    def save_model(self, request: HttpRequest, obj: Model, form: Form, change: Any) -> None:
        if "password" in form.changed_data:
            obj.set_password(form.cleaned_data.get("password")) # type: ignore
        
        return super().save_model(request, obj, form, change)

