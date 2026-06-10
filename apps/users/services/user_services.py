from django.db import transaction
from django.contrib.auth import get_user_model
from ..models.role import StaffRole

User = get_user_model()

@transaction.atomic
def update_user_role(*, user: User, role: StaffRole) -> User:
    """Service to safely update a user's role."""
    user.role = role
    
    # If a role is assigned, ensure is_staff is True
    if role:
        user.is_staff = True
        
    user.save()
    return user

@transaction.atomic
def deactivate_user(*, user: User) -> User:
    """Service to deactivate a user."""
    user.is_active = False
    user.save()
    return user
