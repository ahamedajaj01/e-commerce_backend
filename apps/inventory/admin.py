from django.contrib import admin
from .models.inventory import StockMovement

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('id', 'variant', 'quantity', 'movement_type', 'created_at')
