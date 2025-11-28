from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from . import models

# Register your models here.
@admin.register(models.Member)
class MemberAdmin(UnfoldModelAdmin):
    list_display = ("id", "name", "email", "track", "code", "collage_code", "phone_number")
    search_fields = ("name", "code", "collage_code", "phone_number")
