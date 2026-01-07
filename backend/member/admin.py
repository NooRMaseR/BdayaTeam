from unfold.contrib.filters.admin.dropdown_filters import ChoicesDropdownFilter
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Member)
class MemberAdmin(UnfoldModelAdmin):
    list_display = ("code", "name", "email", "track", "status", "collage_code", "phone_number", "joined_at")
    search_fields = ("name", "code", "collage_code", "phone_number")
    list_display_links = ("name", "code", "email")
    list_per_page = 20
    ordering = ("track", "-joined_at")
    list_filter = (
        ("track", ChoicesDropdownFilter),
    )
    list_filter_submit = True
    
@admin.register(models.ReciviedTask)
class RecivedTaskAdmin(UnfoldModelAdmin):
    list_display = ("task", "member", "track", "degree", "signed")
    list_display_links = ("task", "member")
    
@admin.register(models.ReciviedTaskFile)
class RecivedTaskFileAdmin(UnfoldModelAdmin):
    list_display = ("id", "recivied_task", "recivied_task__member__name", "recivied_task__member__code")
    list_display_links = ("id", "recivied_task", "recivied_task__member__name")