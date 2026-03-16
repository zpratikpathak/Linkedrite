import uuid
import logging

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from . import services
from .models import LinkedInAccount

logger = logging.getLogger(__name__)


@login_required
def connect(request):
    """Initiate LinkedIn OAuth flow."""
    state = str(uuid.uuid4())
    request.session['linkedin_oauth_state'] = state
    auth_url = services.build_authorization_url(state)
    return redirect(auth_url)


@login_required
def callback(request):
    """Handle LinkedIn OAuth callback."""
    error = request.GET.get('error')
    if error:
        messages.error(request, f'LinkedIn authorization failed: {error}')
        return redirect('linkedin:accounts')

    code = request.GET.get('code')
    state = request.GET.get('state')
    saved_state = request.session.pop('linkedin_oauth_state', None)

    if not code or state != saved_state:
        messages.error(request, 'Invalid OAuth state. Please try again.')
        return redirect('linkedin:accounts')

    try:
        token_data = services.exchange_code_for_token(code)
        profile_data = services.fetch_user_profile(token_data['access_token'])
        services.save_linkedin_account(request.user, token_data, profile_data)
        messages.success(request, 'LinkedIn account connected successfully!')
    except Exception:
        logger.exception('LinkedIn OAuth callback failed')
        messages.error(request, 'Failed to connect LinkedIn account. Please try again.')

    return redirect('linkedin:accounts')


@login_required
def accounts_list(request):
    """List all connected LinkedIn accounts for the current user."""
    linked_accounts = LinkedInAccount.objects.filter(user=request.user, is_active=True)
    return render(request, 'linkedin/accounts.html', {'linked_accounts': linked_accounts})


@login_required
def disconnect(request, account_id):
    """Disconnect a LinkedIn account."""
    if request.method != 'POST':
        return redirect('linkedin:accounts')

    account = get_object_or_404(LinkedInAccount, id=account_id, user=request.user)
    account.is_active = False
    account.save()
    messages.success(request, f'Disconnected {account.display_name}.')
    return redirect('linkedin:accounts')


@login_required
def accounts_json(request):
    """Return connected accounts as JSON (for Alpine.js AJAX)."""
    linked_accounts = LinkedInAccount.objects.filter(user=request.user, is_active=True)
    data = [
        {
            'id': a.id,
            'display_name': a.display_name,
            'profile_picture_url': a.profile_picture_url,
            'is_token_valid': a.is_token_valid(),
        }
        for a in linked_accounts
    ]
    return JsonResponse({'accounts': data})
