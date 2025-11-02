"""
Management command to create a default admin account.

This command creates a default superuser account for initial system setup.
The default credentials should be changed immediately after first login.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    """
    Django management command to create a default admin account.

    Usage:
        python manage.py create_default_admin

    This creates an admin account with default credentials:
        Username: admin
        Password: admin123
        Email: admin@meetingcalendar.local

    WARNING: These default credentials should be changed immediately
    after first login for security reasons.
    """
    help = 'Creates a default admin account if it does not exist'

    def handle(self, *args, **kwargs):
        """
        Execute the management command.

        Creates a superuser account with default credentials if no user
        with username 'admin' exists.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        username = 'admin'
        email = 'admin@meetingcalendar.local'
        password = 'admin123'

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(
                    f'Admin user "{username}" already exists. Skipping creation.'
                )
            )
            return

        try:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created admin user: {username}'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '\n' + '='*70
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'DEFAULT ADMIN CREDENTIALS:'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f'  Username: {username}'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    f'  Password: {password}'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '='*70
                )
            )
            self.stdout.write(
                self.style.ERROR(
                    '\nWARNING: Change these credentials immediately after login!'
                )
            )
            self.stdout.write(
                self.style.ERROR(
                    'Access your account at /account/ to update your password.'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Error creating admin user: {str(e)}'
                )
            )
