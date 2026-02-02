from unfold.admin import ModelAdmin as UnfoldModelAdmin, StackedInline
from unfold.paginator import InfinitePaginator
from django.contrib import admin
from . import models


# Register your models here.

@admin.register(models.Task)
class TaskAdmin(UnfoldModelAdmin):
    list_display = ("id", "task_number", "track", "created_at", "expires_at", "is_expired")
    list_display_links = ("id", "task_number", "track")
    search_fields = ("task_number",)
    paginator = InfinitePaginator
    list_per_page = 50
