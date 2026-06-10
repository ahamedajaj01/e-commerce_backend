from django.db import transaction
from ..models.inventory import StockMovement
from apps.catalog.models.product import ProductVariant

@transaction.atomic
def adjust_inventory(*, variant: ProductVariant, quantity: int, movement_type: str, note: str = "") -> ProductVariant:
    """Main service for all inventory adjustments."""
    
    if movement_type in [StockMovement.MovementType.IN, StockMovement.MovementType.RETURN, StockMovement.MovementType.ADJUSTMENT]:
        variant.stock_quantity += quantity
    elif movement_type == StockMovement.MovementType.OUT:
        variant.stock_quantity -= quantity
        # Prevent negative stock, optionally you can set to 0 based on business logic
        if variant.stock_quantity < 0:
            variant.stock_quantity = 0
            
    variant.save()
    
    StockMovement.objects.create(
        variant=variant,
        quantity=quantity,
        movement_type=movement_type,
        note=note
    )
    
    return variant
