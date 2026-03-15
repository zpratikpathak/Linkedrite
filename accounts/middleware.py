"""
Middleware for admin account sync and email verification enforcement.
"""
import os
import threading
from django.core.management import call_command
from django.shortcuts import redirect
from django.urls import reverse
from io import StringIO
import sys


VERIFICATION_EXEMPT_PATHS = [
    '/accounts/verify-email/',
    '/accounts/resend-verification/',
    '/accounts/logout/',
    '/accounts/login/',
    '/accounts/signup/',
    '/accounts/password-reset/',
    '/accounts/profile/',
    '/admin/',
    '/static/',
    '/favicon.ico',
]


class EmailVerificationMiddleware:
    """Redirects authenticated but unverified users to the verification page."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and not request.user.email_verified
            and not self._is_exempt(request.path)
        ):
            return redirect('accounts:verify_email_required')

        return self.get_response(request)

    def _is_exempt(self, path):
        return any(path.startswith(p) for p in VERIFICATION_EXEMPT_PATHS)


class AdminAccountSyncMiddleware:
    """Middleware that syncs admin account with .env on first request"""
    
    _sync_done = False
    _lock = threading.Lock()
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Sync admin account on first request
        if not AdminAccountSyncMiddleware._sync_done:
            with AdminAccountSyncMiddleware._lock:
                if not AdminAccountSyncMiddleware._sync_done:
                    self.sync_admin_account()
                    AdminAccountSyncMiddleware._sync_done = True
        
        response = self.get_response(request)
        return response
    
    def sync_admin_account(self):
        """Sync admin account with environment variables"""
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        
        if not admin_email or not admin_password:
            return
        
        try:
            # Capture output
            original_stdout = sys.stdout
            sys.stdout = StringIO()
            
            call_command('create_default_admin')
            output = sys.stdout.getvalue()
            sys.stdout = original_stdout
            
            # Only print if there's an actual update
            if 'Updated' in output or 'Created' in output:
                print(f"[LinkedRite] Admin account synced with .env credentials: {admin_email}")
                
        except Exception as e:
            sys.stdout = original_stdout
            # Silently handle errors - don't break the request
            pass

