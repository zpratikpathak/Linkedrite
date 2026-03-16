import json
import logging
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from linkedin.models import LinkedInAccount
from .models import Post, PostImage, PostStatus
from . import services
from .tasks import publish_post_task

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """Main dashboard with overview."""
    posts = Post.objects.filter(user=request.user)[:10]
    linked_accounts = LinkedInAccount.objects.filter(user=request.user, is_active=True)

    stats = {
        'total_posts': Post.objects.filter(user=request.user).count(),
        'published': Post.objects.filter(user=request.user, status=PostStatus.PUBLISHED).count(),
        'scheduled': Post.objects.filter(user=request.user, status=PostStatus.SCHEDULED).count(),
        'drafts': Post.objects.filter(user=request.user, status=PostStatus.DRAFT).count(),
        'accounts': linked_accounts.count(),
    }

    return render(request, 'posts/dashboard.html', {
        'posts': posts,
        'linked_accounts': linked_accounts,
        'stats': stats,
    })


@login_required
def post_list(request):
    """List all posts with optional status filter."""
    status_filter = request.GET.get('status', '')
    posts = Post.objects.filter(user=request.user)
    if status_filter and status_filter in PostStatus.values:
        posts = posts.filter(status=status_filter)

    return render(request, 'posts/list.html', {
        'posts': posts,
        'current_filter': status_filter,
        'statuses': PostStatus.choices,
    })


@login_required
def post_create(request):
    """Create a new post (composer page)."""
    linked_accounts = LinkedInAccount.objects.filter(user=request.user, is_active=True)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        account_id = request.POST.get('linkedin_account')
        action = request.POST.get('action', 'draft')

        if not content:
            messages.error(request, 'Post content cannot be empty.')
            return render(request, 'posts/composer.html', {'linked_accounts': linked_accounts})

        account = None
        if account_id:
            account = LinkedInAccount.objects.filter(id=account_id, user=request.user, is_active=True).first()

        post = Post.objects.create(
            user=request.user,
            linkedin_account=account,
            content=content,
            status=PostStatus.DRAFT,
        )

        uploaded_image = request.FILES.get('image')
        if uploaded_image:
            PostImage.objects.create(
                post=post,
                image=uploaded_image,
                alt_text=request.POST.get('alt_text', ''),
            )

        if action == 'publish':
            if not account:
                messages.error(request, 'Select a LinkedIn account to publish.')
                return redirect('posts:edit', post_id=post.id)
            post.status = PostStatus.PUBLISHING
            post.save()
            publish_post_task.delay(post.id)
            messages.success(request, 'Post is being published to LinkedIn!')
            return redirect('posts:detail', post_id=post.id)

        elif action == 'schedule':
            schedule_time = request.POST.get('scheduled_at')
            if not schedule_time or not account:
                messages.error(request, 'Select an account and schedule time.')
                return redirect('posts:edit', post_id=post.id)
            post.scheduled_at = datetime.fromisoformat(schedule_time)
            post.status = PostStatus.SCHEDULED
            post.save()
            messages.success(request, 'Post scheduled successfully!')
            return redirect('posts:detail', post_id=post.id)

        else:
            messages.success(request, 'Draft saved.')
            return redirect('posts:edit', post_id=post.id)

    return render(request, 'posts/composer.html', {'linked_accounts': linked_accounts})


@login_required
def post_edit(request, post_id):
    """Edit an existing post."""
    post = get_object_or_404(Post, id=post_id, user=request.user)
    linked_accounts = LinkedInAccount.objects.filter(user=request.user, is_active=True)

    if post.status == PostStatus.PUBLISHED:
        messages.warning(request, 'Published posts cannot be edited.')
        return redirect('posts:detail', post_id=post.id)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        account_id = request.POST.get('linkedin_account')
        action = request.POST.get('action', 'draft')

        post.content = content
        account = None
        if account_id:
            account = LinkedInAccount.objects.filter(id=account_id, user=request.user, is_active=True).first()
            post.linkedin_account = account

        uploaded_image = request.FILES.get('image')
        if uploaded_image:
            post.images.all().delete()
            PostImage.objects.create(
                post=post,
                image=uploaded_image,
                alt_text=request.POST.get('alt_text', ''),
            )

        if action == 'publish':
            if not account:
                messages.error(request, 'Select a LinkedIn account to publish.')
                post.save()
                return redirect('posts:edit', post_id=post.id)
            post.status = PostStatus.PUBLISHING
            post.save()
            publish_post_task.delay(post.id)
            messages.success(request, 'Post is being published to LinkedIn!')
            return redirect('posts:detail', post_id=post.id)

        elif action == 'schedule':
            schedule_time = request.POST.get('scheduled_at')
            if not schedule_time or not account:
                messages.error(request, 'Select an account and schedule time.')
                post.save()
                return redirect('posts:edit', post_id=post.id)
            post.scheduled_at = datetime.fromisoformat(schedule_time)
            post.status = PostStatus.SCHEDULED
            post.save()
            messages.success(request, 'Post scheduled successfully!')
            return redirect('posts:detail', post_id=post.id)

        else:
            post.status = PostStatus.DRAFT
            post.save()
            messages.success(request, 'Draft saved.')
            return redirect('posts:edit', post_id=post.id)

    return render(request, 'posts/composer.html', {
        'post': post,
        'linked_accounts': linked_accounts,
        'editing': True,
    })


@login_required
def post_detail(request, post_id):
    """View a single post."""
    post = get_object_or_404(Post, id=post_id, user=request.user)
    return render(request, 'posts/detail.html', {'post': post})


@login_required
@require_POST
def post_delete(request, post_id):
    """Delete a post."""
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if post.status == PostStatus.PUBLISHED:
        messages.warning(request, 'Published posts cannot be deleted.')
        return redirect('posts:detail', post_id=post.id)
    post.delete()
    messages.success(request, 'Post deleted.')
    return redirect('posts:list')


@login_required
def calendar_view(request):
    """Calendar view of scheduled and published posts."""
    posts = Post.objects.filter(
        user=request.user,
        status__in=[PostStatus.SCHEDULED, PostStatus.PUBLISHED],
    ).values('id', 'content', 'status', 'scheduled_at', 'published_at')

    events = []
    for p in posts:
        dt = p['published_at'] or p['scheduled_at']
        if dt:
            events.append({
                'id': p['id'],
                'title': (p['content'][:50] + '...') if len(p['content']) > 50 else p['content'],
                'date': dt.isoformat(),
                'status': p['status'],
            })

    return render(request, 'posts/calendar.html', {'events_json': json.dumps(events)})


@login_required
@require_POST
def ai_generate_text(request):
    """AJAX endpoint: generate post text with AI."""
    try:
        body = json.loads(request.body)
        topic = body.get('topic', '').strip()
        tone = body.get('tone', 'professional').strip()
        extra = body.get('extra_instructions', '').strip()

        if not topic:
            return JsonResponse({'error': 'Topic is required.'}, status=400)

        text = services.generate_post_text(topic, tone, extra)
        return JsonResponse({'text': text})
    except Exception as exc:
        logger.exception('AI text generation failed')
        return JsonResponse({'error': str(exc)}, status=500)


@login_required
@require_POST
def ai_generate_image(request):
    """AJAX endpoint: generate an image with AI and optionally attach to a post."""
    try:
        body = json.loads(request.body)
        prompt = body.get('prompt', '').strip()
        post_id = body.get('post_id')

        if not prompt:
            return JsonResponse({'error': 'Prompt is required.'}, status=400)

        image_bytes, filename = services.generate_image(prompt)

        if post_id:
            post = get_object_or_404(Post, id=post_id, user=request.user)
            post_image = services.save_generated_image(post, image_bytes, filename, prompt)
            return JsonResponse({
                'image_url': post_image.image.url,
                'image_id': post_image.id,
            })

        import base64
        b64 = base64.b64encode(image_bytes).decode()
        return JsonResponse({
            'image_data': f'data:image/png;base64,{b64}',
            'filename': filename,
        })
    except Exception as exc:
        logger.exception('AI image generation failed')
        return JsonResponse({'error': str(exc)}, status=500)
