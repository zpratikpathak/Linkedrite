from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import pytz
import uuid
from datetime import datetime, timedelta


class CustomUser(AbstractUser):
    """Custom user model with email as the primary identifier"""
    email = models.EmailField(unique=True)
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        choices=[(tz, tz) for tz in pytz.all_timezones],
        help_text="User's timezone for daily limit resets"
    )
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def get_local_time(self):
        """Get current time in user's timezone"""
        user_tz = pytz.timezone(self.timezone)
        return timezone.now().astimezone(user_tz)
    
    def get_midnight_utc(self):
        """Get the next midnight in user's timezone converted to UTC"""
        user_tz = pytz.timezone(self.timezone)
        local_time = timezone.now().astimezone(user_tz)
        # Get midnight of the next day
        midnight = (local_time + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        # Convert back to UTC
        return midnight.astimezone(pytz.UTC)


class EmailVerificationToken(models.Model):
    """Token for email verification"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Token for {self.user.email}"


class PasswordResetToken(models.Model):
    """Token for password reset"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
    
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Reset token for {self.user.email}"