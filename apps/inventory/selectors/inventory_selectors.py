from django.db.models import QuerySet
from ..models.inventory import StockMovement
from apps.catalog.models.product import ProductVariant

def get_low_stock_variants(threshold: int = 5) -> QuerySet:
    return ProductVariant.objects.filter(stock_quantity__lte=threshold).select_related('product')

def get_all_inventory(product_type: str = None, search: str = None) -> QuerySet:
    """
    Returns a QuerySet of variants for the inventory studio with optional search.
    """
    qs = ProductVariant.objects.filter(
        product__is_visible=True
    ).select_related('product').prefetch_related('product__media').order_by('-updated_at')

    if search:
        from django.db.models import Q
        qs = qs.filter(
            Q(sku__icontains=search) | 
            Q(product__name__icontains=search)
        )
    
    return qs

def get_stock_movements(variant_id) -> QuerySet:
    return StockMovement.objects.filter(variant_id=variant_id).order_by('-created_at')
