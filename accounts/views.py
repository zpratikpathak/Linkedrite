from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .forms import (
    SignUpForm, CustomAuthenticationForm, PasswordResetRequestForm,
    SetNewPasswordForm, UserProfileForm
)
from .models import CustomUser, EmailVerificationToken, PasswordResetToken
from subscriptions.models import Subscription, SubscriptionPlan


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('rewrite:dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # We'll send verification email but allow login
            user.save()
            
            # Create free subscription
            Subscription.objects.create(
                user=user,
                plan=SubscriptionPlan.FREE
            )
            
            # Create and send verification token
            token = EmailVerificationToken.objects.create(user=user)
            
            # Send verification email
            subject = 'Verify your LinkedRite account'
            html_message = render_to_string('accounts/email/verify_email.html', {
                'user': user,
                'token': token.token,
                'domain': request.get_host(),
                'protocol': 'https' if request.is_secure() else 'http'
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # Log the user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Account created successfully! Please check your email to verify your account.')
            return redirect('rewrite:dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('rewrite:dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Redirect to next URL or dashboard
            next_url = request.GET.get('next', 'rewrite:dashboard')
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('rewrite:index')


def verify_email(request, token):
    verification = get_object_or_404(EmailVerificationToken, token=token)
    
    if verification.is_valid():
        user = verification.user
        user.email_verified = True
        user.save()
        
        verification.is_used = True
        verification.save()
        
        messages.success(request, 'Your email has been verified successfully!')
        
        if request.user.is_authenticated:
            return redirect('rewrite:dashboard')
        else:
            return redirect('accounts:login')
    else:
        messages.error(request, 'This verification link has expired or has already been used.')
        return redirect('rewrite:index')


@login_required
def resend_verification(request):
    if request.user.email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('dashboard')
    
    # Invalidate old tokens
    EmailVerificationToken.objects.filter(
        user=request.user,
        is_used=False
    ).update(is_used=True)
    
    # Create new token
    token = EmailVerificationToken.objects.create(user=request.user)
    
    # Send verification email
    subject = 'Verify your LinkedRite account'
    html_message = render_to_string('accounts/email/verify_email.html', {
        'user': request.user,
        'token': token.token,
        'domain': request.get_host(),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
        html_message=html_message,
        fail_silently=False,
    )
    
    messages.success(request, 'Verification email sent! Please check your inbox.')
    return redirect('dashboard')


def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email)
            
            # Invalidate old tokens
            PasswordResetToken.objects.filter(
                user=user,
                is_used=False
            ).update(is_used=True)
            
            # Create new token
            token = PasswordResetToken.objects.create(user=user)
            
            # Send reset email
            subject = 'Reset your LinkedRite password'
            html_message = render_to_string('accounts/email/password_reset.html', {
                'user': user,
                'token': token.token,
                'domain': request.get_host(),
                'protocol': 'https' if request.is_secure() else 'http'
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(request, 'Password reset link sent! Please check your email.')
            return redirect('accounts:login')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'accounts/password_reset.html', {'form': form})


def password_reset_confirm(request, token):
    reset_token = get_object_or_404(PasswordResetToken, token=token)
    
    if not reset_token.is_valid():
        messages.error(request, 'This password reset link has expired or has already been used.')
        return redirect('accounts:password_reset')
    
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            reset_token.is_used = True
            reset_token.save()
            
            messages.success(request, 'Your password has been reset successfully! You can now log in.')
            return redirect('accounts:login')
    else:
        form = SetNewPasswordForm()
    
    return render(request, 'accounts/password_reset_confirm.html', {
        'form': form,
        'token': token
    })


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': request.user
    })