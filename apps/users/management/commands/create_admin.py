"""
Django management command for creating super admin user.

This command bootstraps the initial admin user from environment variables.
It's idempotent and safe to run multiple times.

Usage:
    python manage.py create_admin
"""

from django.core.management.base import BaseCommand

from core.bootstrap.admin_initializer import BootstrapAdminService


class Command(BaseCommand):
    """
    Management command to bootstrap super admin user.
    
    This command is thin and delegates all business logic to BootstrapAdminService.
    It focuses on CLI concerns: input/output, styling, and error handling.
    """

    help = 'Create a super admin user from environment variables'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force admin creation (not implemented - use for future features)',
        )

    def handle(self, *args, **options):
        """
        Execute the command.
        
        Args:
            *args: Positional arguments
            **options: Named arguments including --force flag
        """
        self.stdout.write(
            self.style.HTTP_INFO('🚀 Starting admin bootstrap process...\n')
        )

        try:
            # Call the service to ensure super admin exists
            status = BootstrapAdminService.ensure_super_admin()

            # Handle the response based on status type
            if status.status_type == 'created':
                self._output_success(status)
            
            elif status.status_type == 'already_exists':
                self._output_warning(status)
            
            else:  # error
                self._output_error(status)
                raise SystemExit(1)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Unexpected error: {str(e)}')
            )
            raise SystemExit(1)

    def _output_success(self, status):
        """Output success message with styling."""
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Success!\n'
                f'   {status.message}\n'
                f'   Username: {status.admin_username}\n'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                '✅ You can now log in to the admin panel at /admin/\n'
            )
        )

    def _output_warning(self, status):
        """Output warning message with styling."""
        self.stdout.write(
            self.style.WARNING(
                f'⚠️  Admin Already Exists\n'
                f'   {status.message}\n'
                f'   Username: {status.admin_username}\n'
            )
        )

    def _output_error(self, status):
        """Output error message with styling."""
        self.stdout.write(
            self.style.ERROR(
                f'❌ Error!\n'
                f'   {status.message}\n'
            )
        )
