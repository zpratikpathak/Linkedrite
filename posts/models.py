from django.db import models
from django.conf import settings


class PostStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SCHEDULED = 'scheduled', 'Scheduled'
    PUBLISHING = 'publishing', 'Publishing'
    PUBLISHED = 'published', 'Published'
    FAILED = 'failed', 'Failed'


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts',
    )
    linkedin_account = models.ForeignKey(
        'linkedin.LinkedInAccount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
    )
    content = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.DRAFT,
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    linkedin_post_id = models.CharField(max_length=255, blank=True, default='')
    error_message = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        preview = self.content[:60] + '...' if len(self.content) > 60 else self.content
        return f"[{self.get_status_display()}] {preview}"


def post_image_upload_path(instance, filename):
    return f'post_images/{instance.post.user.id}/{filename}'


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=post_image_upload_path)
    alt_text = models.CharField(max_length=500, blank=True, default='')
    prompt = models.TextField(blank=True, default='')
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for post {self.post.id}"
