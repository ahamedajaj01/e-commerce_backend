"""
Admin initialization bootstrap service.

This module provides a reusable service layer for initializing admin users.
It handles all business logic related to admin user creation and validation,
keeping the management command thin and focused on CLI concerns.
"""

from typing import Dict, Literal
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from core.config.env import EnvConfig, AdminCredentials


User = get_user_model()


class AdminInitializationError(Exception):
    """Raised when admin initialization fails."""
    pass


class AdminInitializationStatus:
    """
    Structured response object for admin initialization.
    
    Provides consistent status information to callers.
    """

    def __init__(
        self,
        success: bool,
        message: str,
        status_type: Literal['created', 'already_exists', 'error', 'warning'],
        admin_username: str = '',
    ):
        """
        Initialize status object.
        
        Args:
            success: Whether operation succeeded
            message: Human-readable message
            status_type: Type of status (created, already_exists, error, warning)
            admin_username: Username of the admin (if applicable)
        """
        self.success = success
        self.message = message
        self.status_type = status_type
        self.admin_username = admin_username

    def __repr__(self) -> str:
        """Return string representation of status."""
        return (
            f"AdminInitializationStatus(success={self.success}, "
            f"status_type='{self.status_type}', message='{self.message}')"
        )


class BootstrapAdminService:
    """
    Service layer for admin user initialization.
    
    This service is reusable from various bootstrap flows and ensures
    idempotent admin creation with proper validation and error handling.
    
    Design principles:
    - Single responsibility: Only handles admin initialization
    - Reusability: Can be called from management commands, scripts, or tests
    - Idempotency: Safe to call multiple times
    - Clear contracts: Returns structured status objects
    - No side effects: Doesn't directly log or write to output
    """

    @staticmethod
    def load_credentials_from_env() -> AdminCredentials:
        """
        Load admin credentials from environment.
        
        Returns:
            AdminCredentials: Validated credentials object
            
        Raises:
            AdminInitializationError: If credentials are invalid or missing
        """
        try:
            username = EnvConfig.get_admin_username()
            email = EnvConfig.get_admin_email()
            password = EnvConfig.get_admin_password()
            first_name = EnvConfig.get_admin_first_name()
            last_name = EnvConfig.get_admin_last_name()
            
            return AdminCredentials(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
        except ValueError as e:
            raise AdminInitializationError(f'Credential validation failed: {str(e)}')
        except Exception as e:
            raise AdminInitializationError(f'Failed to load credentials: {str(e)}')

    @staticmethod
    def admin_exists(email: str) -> bool:
        """
        Check if admin user already exists.
        
        Checks email to prevent duplicates.
        
        Args:
            email: Email to check
            
        Returns:
            bool: True if admin exists, False otherwise
        """
        return User.objects.filter(email=email).exists()

    @staticmethod
    def ensure_super_admin() -> AdminInitializationStatus:
        """
        Ensure super admin user exists.
        
        This is the main entry point for admin initialization.
        It's fully idempotent and safe to call multiple times.
        
        Returns:
            AdminInitializationStatus: Status of initialization attempt
            
        Example:
            >>> status = BootstrapAdminService.ensure_super_admin()
            >>> if status.success:
            ...     print(f"Admin created: {status.admin_username}")
        """
        try:
            # Load credentials from environment
            credentials = BootstrapAdminService.load_credentials_from_env()
            
            # Check if admin already exists
            if BootstrapAdminService.admin_exists(credentials.email):
                return AdminInitializationStatus(
                    success=True,
                    message=(
                        f"Super admin '{credentials.email}' already exists. "
                        f"Skipping creation."
                    ),
                    status_type='already_exists',
                    admin_username=credentials.email,
                )
            
            # Create the super admin
            try:
                admin = User.objects.create_superuser(
                    email=credentials.email,
                    password=credentials.password,
                )
                
                return AdminInitializationStatus(
                    success=True,
                    message=(
                        f"Super admin created successfully. "
                        f"Email: {credentials.email}"
                    ),
                    status_type='created',
                    admin_username=credentials.email,
                )
            
            except IntegrityError as e:
                # Race condition: Another process created the admin
                return AdminInitializationStatus(
                    success=True,
                    message=(
                        f"Super admin '{credentials.email}' already exists "
                        f"(created by concurrent process). Skipping creation."
                    ),
                    status_type='already_exists',
                    admin_username=credentials.email,
                )
        
        except AdminInitializationError as e:
            return AdminInitializationStatus(
                success=False,
                message=f"Admin initialization failed: {str(e)}",
                status_type='error',
            )
        
        except Exception as e:
            return AdminInitializationStatus(
                success=False,
                message=f"Unexpected error during admin initialization: {str(e)}",
                status_type='error',
            )

    @staticmethod
    def create_admin_with_credentials(
        credentials: AdminCredentials,
    ) -> AdminInitializationStatus:
        """
        Create admin user with provided credentials.
        
        This is useful when credentials are obtained from other sources
        besides environment variables.
        
        Args:
            credentials: Pre-validated AdminCredentials object
            
        Returns:
            AdminInitializationStatus: Status of creation attempt
        """
        try:
            if BootstrapAdminService.admin_exists(credentials.email):
                return AdminInitializationStatus(
                    success=True,
                    message=f"Admin '{credentials.email}' already exists.",
                    status_type='already_exists',
                    admin_username=credentials.email,
                )
            
            User.objects.create_superuser(
                email=credentials.email,
                password=credentials.password,
            )
            
            return AdminInitializationStatus(
                success=True,
                message=f"Admin '{credentials.email}' created successfully.",
                status_type='created',
                admin_username=credentials.email,
            )
        
        except AdminInitializationError as e:
            return AdminInitializationStatus(
                success=False,
                message=str(e),
                status_type='error',
            )
        
        except IntegrityError:
            return AdminInitializationStatus(
                success=True,
                message=f"Admin '{credentials.email}' already exists.",
                status_type='already_exists',
                admin_username=credentials.email,
            )
        
        except Exception as e:
            return AdminInitializationStatus(
                success=False,
                message=f"Error creating admin: {str(e)}",
                status_type='error',
            )
