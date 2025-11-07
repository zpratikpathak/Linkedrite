from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import pytz


class SubscriptionPlan(models.TextChoices):
    FREE = "FREE", "Free Plan"
    PREMIUM = "PREMIUM", "Premium Plan"


class Subscription(models.Model):
    """User subscription model"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    plan = models.CharField(
        max_length=20,
        choices=SubscriptionPlan.choices,
        default=SubscriptionPlan.FREE
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Payment information for future integration
    stripe_customer_id = models.CharField(max_length=255, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_plan_display()}"
    
    def is_premium(self):
        return self.plan == SubscriptionPlan.PREMIUM and self.is_active
    
    def get_daily_limit(self):
        """Get daily rewrite limit based on plan"""
        if self.plan == SubscriptionPlan.PREMIUM:
            return None  # Unlimited
        return 20  # Free plan limit


class UsageTracking(models.Model):
    """Track daily usage per user"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='usage_records'
    )
    date = models.DateField()
    count = models.IntegerField(default=0)
    reset_time = models.DateTimeField()
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.email} - {self.date} - {self.count} uses"
    
    @classmethod
    def get_or_create_today(cls, user):
        """Get or create usage record for today in user's timezone"""
        user_tz = pytz.timezone(user.timezone)
        local_time = timezone.now().astimezone(user_tz)
        local_date = local_time.date()
        
        # Check if we need to create a new record
        usage, created = cls.objects.get_or_create(
            user=user,
            date=local_date,
            defaults={
                'reset_time': user.get_midnight_utc()
            }
        )
        
        # Check if we need to reset (past the reset time)
        if timezone.now() >= usage.reset_time:
            # Create new record for the new day
            new_date = timezone.now().astimezone(user_tz).date()
            usage, created = cls.objects.get_or_create(
                user=user,
                date=new_date,
                defaults={
                    'reset_time': user.get_midnight_utc()
                }
            )
        
        return usage
    
    def can_use(self):
        """Check if user can make another rewrite"""
        subscription = getattr(self.user, 'subscription', None)
        if not subscription:
            # Create default free subscription
            from .models import Subscription, SubscriptionPlan
            subscription = Subscription.objects.create(
                user=self.user,
                plan=SubscriptionPlan.FREE
            )
        
        daily_limit = subscription.get_daily_limit()
        if daily_limit is None:  # Premium user
            return True
        
        return self.count < daily_limit
    
    def increment(self):
        """Increment usage count"""
        self.count += 1
        self.save()
        return self.count


class Payment(models.Model):
    """Payment records for future integration"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - ${self.amount} - {self.status}"