"""
Django management command to create or update default admin account from environment variables.

This command is safe to run multiple times - it will update existing admin or create new one.
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from subscriptions.models import Subscription, SubscriptionPlan
import pytz

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates or updates default admin account from environment variables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update-existing',
            type=str,
            help='Update an existing admin by email (useful when changing ADMIN_EMAIL)',
        )

    def handle(self, *args, **options):
        # Get environment variables
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        admin_first_name = os.getenv('ADMIN_FIRST_NAME', 'Admin')
        admin_last_name = os.getenv('ADMIN_LAST_NAME', 'User')

        # Check if required environment variables are set
        if not admin_email or not admin_password:
            self.stdout.write(
                self.style.WARNING(
                    'ADMIN_EMAIL and ADMIN_PASSWORD environment variables are not set. '
                    'Skipping default admin creation.'
                )
            )
            return

        try:
            with transaction.atomic():
                # Handle updating existing admin with different email
                if options.get('update_existing'):
                    try:
                        admin_user = User.objects.get(email=options['update_existing'])
                        admin_user.email = admin_email
                        admin_user.username = admin_email
                        admin_user.first_name = admin_first_name
                        admin_user.last_name = admin_last_name
                        admin_user.set_password(admin_password)
                        admin_user.save()
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Updated admin email from {options["update_existing"]} to {admin_email}'
                            )
                        )
                        return
                    except User.DoesNotExist:
                        self.stdout.write(
                            self.style.ERROR(f'No admin found with email: {options["update_existing"]}')
                        )
                        return
                
                # Check if admin user already exists
                try:
                    admin_user = User.objects.get(email=admin_email)
                    
                    # Update existing admin
                    admin_user.first_name = admin_first_name
                    admin_user.last_name = admin_last_name
                    admin_user.is_staff = True
                    admin_user.is_superuser = True
                    admin_user.is_active = True
                    admin_user.email_verified = True
                    
                    # Always update password when environment variable is set
                    # This ensures the admin can always login with the password in .env
                    admin_user.set_password(admin_password)
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated password for admin user: {admin_email}')
                    )
                    
                    admin_user.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated existing admin user: {admin_email}')
                    )
                    
                except User.DoesNotExist:
                    # Create new admin user
                    admin_user = User.objects.create_superuser(
                        email=admin_email,
                        password=admin_password,
                        first_name=admin_first_name,
                        last_name=admin_last_name,
                        username=admin_email,  # Use email as username
                        timezone=pytz.UTC,
                        email_verified=True
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Created new admin user: {admin_email}')
                    )
                
                # Ensure admin has a premium subscription
                subscription, created = Subscription.objects.get_or_create(
                    user=admin_user,
                    defaults={
                        'plan': SubscriptionPlan.PREMIUM,
                        'is_active': True
                    }
                )
                
                if not created and subscription.plan != SubscriptionPlan.PREMIUM:
                    subscription.plan = SubscriptionPlan.PREMIUM
                    subscription.is_active = True
                    subscription.save()
                    self.stdout.write(
                        self.style.SUCCESS('Updated admin subscription to PREMIUM')
                    )
                elif created:
                    self.stdout.write(
                        self.style.SUCCESS('Created PREMIUM subscription for admin')
                    )
                
                # Display summary
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\nAdmin account ready:\n'
                        f'  Email: {admin_email}\n'
                        f'  Name: {admin_first_name} {admin_last_name}\n'
                        f'  Subscription: PREMIUM (unlimited)\n'
                        f'  Status: Active\n'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating/updating admin account: {str(e)}')
            )
            raise
