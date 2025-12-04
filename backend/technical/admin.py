from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline, StackedInline
from core.models import BdayaUser, UserRole
from django.contrib import admin
from . import models


# Register your models here.

class TrackTechnichal(StackedInline):
    model = BdayaUser
    fields = ("username", "email", "phone_number")
    extra = 0
    tab=True
    collapsible=True
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=UserRole.TECHNICAL)
  
@admin.register(models.Track)
class CourseAdmin(UnfoldModelAdmin):
    list_display = ("id", "track", "prefix")
    search_fields = ("track", )
    inlines = [TrackTechnichal]

@admin.register(models.Task)
class TaskAdmin(UnfoldModelAdmin):
    list_display = ("id", "task_number", "track", "created_at", "expires_at", "is_expired")
    search_fields = ("task_number",)
    
