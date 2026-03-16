import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def publish_scheduled_posts():
    """Find all scheduled posts whose time has arrived and publish them."""
    from .models import Post, PostStatus
    from .services import publish_post

    now = timezone.now()
    due_posts = Post.objects.filter(
        status=PostStatus.SCHEDULED,
        scheduled_at__lte=now,
    ).select_related('linkedin_account')

    count = 0
    for post in due_posts:
        logger.info('Publishing scheduled post %s', post.id)
        publish_post(post)
        count += 1

    if count:
        logger.info('Published %d scheduled posts', count)
    return count


@shared_task
def publish_post_task(post_id: int):
    """Publish a single post by ID (for immediate async publishing)."""
    from .models import Post
    from .services import publish_post

    try:
        post = Post.objects.select_related('linkedin_account').get(id=post_id)
        publish_post(post)
    except Post.DoesNotExist:
        logger.error('Post %s not found for publishing', post_id)
