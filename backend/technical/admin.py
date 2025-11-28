from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline
from django.contrib import admin
from . import models


# Register your models here.

class TrackTechnichal(TabularInline):
    model = models.Technical
    tab = True
    extra = 1
    
@admin.register(models.Technical)
class TechnicalAdmin(UnfoldModelAdmin):
    list_display = ("id", "user", "track")
    search_fields = ("track", )
    
@admin.register(models.Track)
class CourseAdmin(UnfoldModelAdmin):
    list_display = ("id", "track", "prefix")
    search_fields = ("track", )
    inlines = [TrackTechnichal]

@admin.register(models.Task)
class TaskAdmin(UnfoldModelAdmin):
    list_display = ("id", "task_number", "track", "uploaded_at")
    search_fields = ("task_number",)
    
