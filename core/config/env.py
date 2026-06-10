"""
Centralized environment configuration using python-decouple.

This module handles all environment variable loading and validation
for the application. It provides type-safe access to environment
variables with sensible defaults.
"""

from typing import Optional
from decouple import config, UndefinedValueError


class EnvConfig:
    """Centralized environment configuration handler."""

    @staticmethod
    def get_admin_username() -> str:
        """
        Get admin username from environment.
        
        Returns:
            str: Admin username
            
        Raises:
            UndefinedValueError: If ADMIN_USERNAME is not set
        """
        try:
            return config('ADMIN_USERNAME')
        except UndefinedValueError:
            raise UndefinedValueError('ADMIN_USERNAME environment variable is required')

    @staticmethod
    def get_admin_email() -> str:
        """
        Get admin email from environment.
        
        Returns:
            str: Admin email address
            
        Raises:
            UndefinedValueError: If ADMIN_EMAIL is not set
        """
        try:
            return config('ADMIN_EMAIL')
        except UndefinedValueError:
            raise UndefinedValueError('ADMIN_EMAIL environment variable is required')

    @staticmethod
    def get_admin_password() -> str:
        """
        Get admin password from environment.
        
        Returns:
            str: Admin password
            
        Raises:
            UndefinedValueError: If ADMIN_PASSWORD is not set
        """
        try:
            return config('ADMIN_PASSWORD')
        except UndefinedValueError:
            raise UndefinedValueError('ADMIN_PASSWORD environment variable is required')

    @staticmethod
    def get_admin_first_name() -> str:
        """
        Get admin first name from environment (optional).
        
        Returns:
            str: Admin first name or empty string
        """
        return config('ADMIN_FIRST_NAME', default='Admin')

    @staticmethod
    def get_admin_last_name() -> str:
        """
        Get admin last name from environment (optional).
        
        Returns:
            str: Admin last name or empty string
        """
        return config('ADMIN_LAST_NAME', default='User')

    @staticmethod
    def get_debug_mode() -> bool:
        """
        Get debug mode flag.
        
        Returns:
            bool: Debug mode enabled/disabled
        """
        return config('DEBUG', default=False, cast=bool)


class AdminCredentials:
    """
    Immutable admin credentials container.
    
    Validates credentials at instantiation time to fail fast.
    """

    def __init__(
        self,
        username: str,
        email: str,
        password: str,
        first_name: str = '',
        last_name: str = '',
    ):
        """
        Initialize and validate admin credentials.
        
        Args:
            username: Admin username
            email: Admin email address
            password: Admin password
            first_name: Admin first name (optional)
            last_name: Admin last name (optional)
            
        Raises:
            ValueError: If any required field is empty or invalid
        """
        self._validate_credentials(username, email, password)
        
        self.username = username.strip()
        self.email = email.strip().lower()
        self.password = password
        self.first_name = first_name.strip() if first_name else ''
        self.last_name = last_name.strip() if last_name else ''

    @staticmethod
    def _validate_credentials(username: str, email: str, password: str) -> None:
        """
        Validate credentials.
        
        Args:
            username: Username to validate
            email: Email to validate
            password: Password to validate
            
        Raises:
            ValueError: If validation fails
        """
        if not username or not username.strip():
            raise ValueError('Username cannot be empty')
        
        if not email or not email.strip():
            raise ValueError('Email cannot be empty')
        
        if not password:
            raise ValueError('Password cannot be empty')
        
        if len(username) < 3:
            raise ValueError('Username must be at least 3 characters long')
        
        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if '@' not in email or '.' not in email:
            raise ValueError('Email format is invalid')

    def __repr__(self) -> str:
        """Return safe string representation (no password)."""
        return (
            f"AdminCredentials(username='{self.username}', "
            f"email='{self.email}', first_name='{self.first_name}')"
        )
