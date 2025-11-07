"""
Example: How to use Redis caching in LinkedRite

This file shows examples of using Django's cache framework with Redis.
"""

from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
import time


# 1. Basic cache usage in a function
def get_user_stats(user_id):
    """Get user statistics with caching."""
    cache_key = f"user_stats_{user_id}"
    
    # Try to get from cache
    stats = cache.get(cache_key)
    
    if stats is None:
        # Not in cache, calculate stats
        print(f"Cache miss for user {user_id}")
        stats = {
            'total_rewrites': calculate_total_rewrites(user_id),
            'monthly_usage': calculate_monthly_usage(user_id),
            'last_active': get_last_active(user_id)
        }
        
        # Store in cache for 5 minutes (300 seconds)
        cache.set(cache_key, stats, timeout=300)
    else:
        print(f"Cache hit for user {user_id}")
    
    return stats


# 2. Using cache decorator on views
@cache_page(60 * 15)  # Cache for 15 minutes
def public_stats_view(request):
    """Public statistics page - good candidate for caching."""
    return JsonResponse({
        'total_users': User.objects.count(),
        'total_rewrites': RewriteHistory.objects.count(),
        'timestamp': time.time()
    })


# 3. Using cache with class-based views
@method_decorator(cache_page(60 * 5), name='get')
class DashboardView(View):
    def get(self, request):
        # This response will be cached for 5 minutes
        return render(request, 'dashboard.html', context)


# 4. Cache invalidation example
def update_user_profile(user_id, new_data):
    """Update user profile and invalidate cache."""
    # Update the database
    user = User.objects.get(id=user_id)
    user.update(**new_data)
    
    # Invalidate the cache
    cache_key = f"user_stats_{user_id}"
    cache.delete(cache_key)
    
    # Or invalidate multiple keys with pattern
    cache.delete_many([
        f"user_stats_{user_id}",
        f"user_profile_{user_id}",
        f"user_settings_{user_id}"
    ])


# 5. Using cache for API rate limiting
def check_api_rate_limit(user_id, limit=100):
    """Simple rate limiting using cache."""
    cache_key = f"api_limit_{user_id}_{time.strftime('%Y%m%d%H')}"
    
    # Get current count
    current_count = cache.get(cache_key, 0)
    
    if current_count >= limit:
        return False, current_count
    
    # Increment and store with 1 hour expiry
    new_count = current_count + 1
    cache.set(cache_key, new_count, timeout=3600)
    
    return True, new_count


# 6. Cache warming example
def warm_popular_caches():
    """Pre-populate cache with frequently accessed data."""
    # Get top users
    top_users = User.objects.filter(
        subscription__plan='PREMIUM'
    ).order_by('-last_login')[:100]
    
    for user in top_users:
        # Pre-calculate and cache their stats
        stats = {
            'total_rewrites': calculate_total_rewrites(user.id),
            'monthly_usage': calculate_monthly_usage(user.id),
        }
        cache.set(f"user_stats_{user.id}", stats, timeout=600)


# 7. Using cache for expensive OpenAI calls
def get_rewrite_with_cache(original_text, include_emoji=True):
    """Cache OpenAI rewrite results to avoid duplicate API calls."""
    # Create a unique cache key based on input parameters
    import hashlib
    text_hash = hashlib.md5(f"{original_text}_{include_emoji}".encode()).hexdigest()
    cache_key = f"rewrite_{text_hash[:12]}"
    
    # Check cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        return {
            'rewritten_text': cached_result,
            'from_cache': True
        }
    
    # Not in cache, call OpenAI
    rewritten_text = call_openai_api(original_text, include_emoji)
    
    # Cache for 24 hours (common rewrites might be repeated)
    cache.set(cache_key, rewritten_text, timeout=86400)
    
    return {
        'rewritten_text': rewritten_text,
        'from_cache': False
    }


# 8. Session-based caching for user preferences
def get_user_preferences(request):
    """Use Redis-backed sessions for fast preference access."""
    # When REDIS_SESSION_BACKEND=True, this uses Redis
    preferences = request.session.get('user_preferences')
    
    if not preferences:
        # Load from database
        user = request.user
        preferences = {
            'theme': user.profile.theme,
            'timezone': str(user.timezone),
            'include_emoji': user.profile.include_emoji_default
        }
        request.session['user_preferences'] = preferences
    
    return preferences


# 9. Cache tags for grouped invalidation (requires django-cachetags)
def get_pricing_plans():
    """Example using cache tags for easier invalidation."""
    from django.core.cache import cache
    from django.core.cache.utils import make_template_fragment_key
    
    cache_key = 'pricing_plans_all'
    plans = cache.get(cache_key)
    
    if not plans:
        plans = list(SubscriptionPlan.objects.all().values())
        # Cache for 1 hour
        cache.set(cache_key, plans, 3600)
    
    return plans


# 10. Conditional caching based on user type
def get_dashboard_data(user):
    """Cache differently based on user type."""
    if user.subscription.plan == 'FREE':
        # Cache free user dashboards longer (less dynamic)
        cache_timeout = 1800  # 30 minutes
        cache_key = f"dashboard_free_{user.id}"
    else:
        # Premium users might have more dynamic data
        cache_timeout = 300  # 5 minutes
        cache_key = f"dashboard_premium_{user.id}"
    
    data = cache.get(cache_key)
    if not data:
        data = generate_dashboard_data(user)
        cache.set(cache_key, data, cache_timeout)
    
    return data


# Settings to add to your views.py:
"""
from django.core.cache import cache
from django.views.decorators.cache import cache_page, cache_control
from django.views.decorators.vary import vary_on_headers

# In your RewriteAPI view, you could add caching:
class RewriteAPI(APIView):
    def post(self, request):
        # ... existing code ...
        
        # Cache frequent rewrites
        cache_key = f"rewrite_{hashlib.md5(original_post.encode()).hexdigest()[:8]}"
        cached = cache.get(cache_key)
        if cached and not request.data.get('force_new'):
            return Response({
                'rewritten_post': cached,
                'from_cache': True,
                'usage': usage_data
            })
        
        # ... call OpenAI ...
        
        # Cache the result
        cache.set(cache_key, rewritten_post, timeout=3600)
"""

