from django.contrib import admin
from .models import Post, PostImage


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'linkedin_account', 'scheduled_at', 'published_at', 'created_at')
    list_filter = ('status',)
    search_fields = ('content', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PostImageInline]


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'is_ai_generated', 'created_at')
    list_filter = ('is_ai_generated',)
    readonly_fields = ('created_at',)
