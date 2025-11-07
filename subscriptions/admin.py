from django.contrib import admin
from django.utils import timezone
from .models import Subscription, UsageTracking, Payment, SubscriptionPlan


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'is_active', 'start_date', 'end_date', 'created_at')
    list_filter = ('plan', 'is_active', 'created_at')
    search_fields = ('user__email', 'user__username', 'stripe_customer_id', 'stripe_subscription_id')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Subscription Details', {
            'fields': ('plan', 'is_active', 'start_date', 'end_date')
        }),
        ('Payment Information', {
            'fields': ('stripe_customer_id', 'stripe_subscription_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['upgrade_to_premium', 'downgrade_to_free']
    
    def upgrade_to_premium(self, request, queryset):
        count = queryset.update(
            plan=SubscriptionPlan.PREMIUM,
            is_active=True,
            updated_at=timezone.now()
        )
        self.message_user(request, f'{count} subscription(s) upgraded to Premium.')
    upgrade_to_premium.short_description = 'Upgrade selected to Premium'
    
    def downgrade_to_free(self, request, queryset):
        count = queryset.update(
            plan=SubscriptionPlan.FREE,
            updated_at=timezone.now()
        )
        self.message_user(request, f'{count} subscription(s) downgraded to Free.')
    downgrade_to_free.short_description = 'Downgrade selected to Free'


@admin.register(UsageTracking)
class UsageTrackingAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'count', 'reset_time', 'get_plan')
    list_filter = ('date', 'user__subscription__plan')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('user', 'date', 'reset_time')
    ordering = ('-date', '-count')
    
    def get_plan(self, obj):
        if hasattr(obj.user, 'subscription'):
            return obj.user.subscription.get_plan_display()
        return 'No subscription'
    get_plan.short_description = 'Plan'
    
    def has_add_permission(self, request):
        # Prevent manual creation of usage records
        return False


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('user__email', 'stripe_payment_intent_id')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        # Payments should be created through the payment system
        return False
    
    def has_change_permission(self, request, obj=None):
        # Payments should not be edited
        return False