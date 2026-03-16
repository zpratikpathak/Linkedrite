from django.contrib import admin
from .models import LinkedInAccount


@admin.register(LinkedInAccount)
class LinkedInAccountAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'linkedin_id', 'is_active', 'token_expires_at', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('display_name', 'user__email', 'linkedin_id')
    readonly_fields = ('created_at', 'updated_at')
