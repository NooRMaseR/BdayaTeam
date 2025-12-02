from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.contrib.filters.admin.dropdown_filters import ChoicesDropdownFilter
from unfold.contrib.filters.admin.choice_filters import CheckboxFilter, RadioFilter, BooleanRadioFilter
from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Member)
class MemberAdmin(UnfoldModelAdmin):
    list_display = ("code", "name", "email", "track", "collage_code", "phone_number")
    search_fields = ("name", "code", "collage_code", "phone_number")
    list_display_links = ("name", "code", "email")
    list_filter = (
        ("track", ChoicesDropdownFilter),
    )
    list_filter_submit = True
    
@admin.register(models.ReciviedTask)
class RecivedTaskAdmin(UnfoldModelAdmin):
    list_display = ("task", "member", "track", "degree", "signed")
    list_display_links = ("task", "member")