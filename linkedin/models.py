from django.db import models
from django.conf import settings
from django.utils import timezone


class LinkedInAccount(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='linkedin_accounts',
    )
    linkedin_id = models.CharField(max_length=255, unique=True)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, default='')
    token_expires_at = models.DateTimeField(null=True, blank=True)
    display_name = models.CharField(max_length=255, blank=True, default='')
    profile_picture_url = models.URLField(max_length=1024, blank=True, default='')
    profile_url = models.URLField(max_length=1024, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.display_name} ({self.user.email})"

    def is_token_valid(self):
        if not self.token_expires_at:
            return False
        return timezone.now() < self.token_expires_at
