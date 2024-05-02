from django.contrib import admin
from .models import APICounter


@admin.register(APICounter)
class APICounterAdmin(admin.ModelAdmin):
    list_display = ("id", "count")
