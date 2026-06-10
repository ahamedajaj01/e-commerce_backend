from django.db import models
from core.common.models.base import BaseModel
from apps.catalog.models.product import ProductVariant

class StockMovement(BaseModel):
    class MovementType(models.TextChoices):
        IN = "IN", "Restock"
        OUT = "OUT", "Sale"
        RESERVE = "RESERVE", "Reservation"
        UNRESERVE = "UNRESERVE", "Unreservation"
        ADJUSTMENT = "ADJUSTMENT", "Adjustment"
        RETURN = "RETURN", "Return"

    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE, 
        related_name='stock_movements'
    )
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    note = models.TextField(blank=True)
    reference_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.movement_type} - {self.variant.sku}: {self.quantity}"
