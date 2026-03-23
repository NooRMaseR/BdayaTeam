from unfold.contrib.filters.admin.dropdown_filters import RelatedDropdownFilter
from unfold.contrib.filters.admin.choice_filters import ChoicesCheckboxFilter
from unfold.contrib.filters.admin.datetime_filters import RangeDateTimeFilter
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.paginator import InfinitePaginator
from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.Member)
class MemberAdmin(UnfoldModelAdmin):
    list_display = ("code", "name", "email", "track", "status", "collage_code", "phone_number", "joined_at")
    search_fields = ("bdaya_user__username", "code", "collage_code", "bdaya_user__phone_number")
    list_display_links = ("name", "code", "email")
    list_per_page = 50
    paginator = InfinitePaginator
    ordering = ("track", "-joined_at")
    list_filter = (
        ("track", RelatedDropdownFilter),
        ("status", ChoicesCheckboxFilter),
        ("joined_at", RangeDateTimeFilter),
    )
    list_select_related = ("bdaya_user", "track")
    list_filter_submit = True
    autocomplete_fields = ("bdaya_user", "track")
    
@admin.register(models.ReciviedTask)
class RecivedTaskAdmin(UnfoldModelAdmin):
    list_display = ("task", "member", "track", "degree", "signed")
    list_display_links = ("task", "member")
    paginator = InfinitePaginator
    list_per_page = 50
    
@admin.register(models.ReciviedTaskFile)
class RecivedTaskFileAdmin(UnfoldModelAdmin):
    list_display = ("id", "recivied_task", "recivied_task__member__bdaya_user__username", "recivied_task__member__code")
    list_display_links = ("id", "recivied_task", "recivied_task__member__bdaya_user__username")
    paginator = InfinitePaginator
    list_per_page = 50