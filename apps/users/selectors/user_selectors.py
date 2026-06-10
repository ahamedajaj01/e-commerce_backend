from typing import Iterable
from django.contrib.auth import get_user_model
from ..models.role import StaffRole

User = get_user_model()

def get_staff_users() -> Iterable[User]:
    """Selector to get all staff users."""
    return User.objects.filter(is_staff=True)

def get_users_by_role(role: StaffRole) -> Iterable[User]:
    """Selector to get users by a specific staff role."""
    return User.objects.filter(role=role)

def get_user_by_email(*, email: str) -> User:
    """Selector to get a user by email."""
    return User.objects.filter(email=email).first()
