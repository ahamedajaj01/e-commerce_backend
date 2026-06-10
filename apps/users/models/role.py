from django.db import models

class StaffRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    INVENTORY = "inventory", "Inventory Staff"
    SUPPORT = "support", "Support Staff"
    MARKETING = "marketing", "Marketing Staff"
    OPERATIONS = "operations", "Operations Staff"
