#!/usr/bin/env python
"""
Quick script to set up a development admin account without using environment variables.
Useful for local development.

Usage:
    python scripts/setup_dev_admin.py
"""

import os
import sys
import django

# Add the project directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Linkedrite.settings')
django.setup()

from django.contrib.auth import get_user_model
from subscriptions.models import Subscription, SubscriptionPlan
import pytz

User = get_user_model()


def create_dev_admin():
    """Create a development admin account with default credentials."""
    admin_email = 'admin@localhost'
    admin_password = 'admin123'
    
    try:
        # Check if admin already exists
        admin = User.objects.filter(email=admin_email).first()
        
        if admin:
            print(f"Admin account already exists: {admin_email}")
            print("Updating password...")
            admin.set_password(admin_password)
            admin.is_staff = True
            admin.is_superuser = True
            admin.is_active = True
            admin.email_verified = True
            admin.save()
        else:
            # Create new admin
            admin = User.objects.create_superuser(
                email=admin_email,
                password=admin_password,
                first_name='Dev',
                last_name='Admin',
                username=admin_email,
                timezone=pytz.UTC,
                email_verified=True
            )
            print(f"Created new admin account: {admin_email}")
        
        # Ensure premium subscription
        subscription, created = Subscription.objects.get_or_create(
            user=admin,
            defaults={
                'plan': SubscriptionPlan.PREMIUM,
                'is_active': True
            }
        )
        
        if not created and subscription.plan != SubscriptionPlan.PREMIUM:
            subscription.plan = SubscriptionPlan.PREMIUM
            subscription.is_active = True
            subscription.save()
        
        print("\n" + "="*50)
        print("Development Admin Account Ready!")
        print("="*50)
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("Plan: PREMIUM (unlimited)")
        print(f"Admin URL: http://localhost:8000/admin/")
        print("="*50)
        print("\n⚠️  WARNING: This account is for development only!")
        print("Never use these credentials in production!")
        
    except Exception as e:
        print(f"Error creating admin: {e}")
        sys.exit(1)


if __name__ == '__main__':
    create_dev_admin()

