from django.db.models import QuerySet
from ..models.product import Product, Category, ProductVariant

def get_active_categories() -> QuerySet:
    return Category.objects.filter(is_active=True, parent=None).prefetch_related('children')

def get_storefront_products(filters: dict = None) -> QuerySet:
    """Public optimized product query with optional filtering."""
    qs = Product.objects.filter(is_active=True, is_visible=True).prefetch_related('variants', 'media').select_related('category')
    
    # GLOBAL KILL SWITCH: If sections are off in Link Studio, hide those products globally
    from apps.cms.models import NavigationItem
    if NavigationItem.objects.filter(title__icontains='trending', is_active=False).exists():
        qs = qs.exclude(is_trending=True)
    if NavigationItem.objects.filter(title__icontains='new', is_active=False).exists():
        qs = qs.exclude(is_new=True)

    if filters:
        category_id = filters.get('category') or filters.get('category_id')
        category_slug = filters.get('category_slug')
        
        if category_id or category_slug:
            category_ids = []
            if category_id:
                # Basic validation for UUID string to prevent 500 errors
                import uuid
                try:
                    uuid.UUID(str(category_id))
                    category_ids.append(category_id)
                    # Include immediate children
                    child_ids = Category.objects.filter(parent_id=category_id).values_list('id', flat=True)
                    category_ids.extend(list(child_ids))
                except (ValueError, TypeError):
                    # If invalid UUID, we can't filter by it, so we either ignore it or return nothing
                    pass
            elif category_slug:
                try:
                    # 1. Fetch the category (must be active in catalog)
                    category = Category.objects.get(slug=category_slug, is_active=True)
                    
                    # 2. CROSS-CHECK with Link Studio (Navigation)
                    # If this category is linked in the Navigation/Link Studio, 
                    # it must be active THERE as well to be served via URL.
                    from apps.cms.models import NavigationItem
                    nav_links = NavigationItem.objects.filter(linked_category=category)
                    if nav_links.exists() and not nav_links.filter(is_active=True).exists():
                        # If links exist but NONE are active, "kill" the URL
                        return qs.none()

                    category_ids.append(category.id)
                    # Only include active children
                    child_ids = Category.objects.filter(parent=category, is_active=True).values_list('id', flat=True)
                    category_ids.extend(list(child_ids))
                except Category.DoesNotExist:
                    return qs.none()
            
            qs = qs.filter(category_id__in=category_ids)
            
        if filters.get('is_new') == 'true':
            qs = qs.filter(is_new=True)
        if filters.get('is_featured') == 'true':
            qs = qs.filter(is_featured=True)
        if filters.get('is_trending') == 'true' or filters.get('category_slug') in ['trending', 'shop-by-video', 'shop-the-look']:
            qs = qs.filter(is_trending=True)
        
        # Brand Filter
        brand_id = filters.get('brand') or filters.get('brand_id')
        if brand_id:
            qs = qs.filter(brand_id=brand_id)
        
        search_query = filters.get('search')
        if search_query:
            from django.db.models import Q
            qs = qs.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            
    return qs

def get_backoffice_products(filters: dict = None) -> QuerySet:
    """Internal admin query with optimized filtering and sorting."""
    qs = Product.objects.filter(is_visible=True).select_related('category', 'brand').prefetch_related('variants', 'media').order_by('-created_at')
    
    if not filters:
        return qs

    # 1. Real-time Search (Name, SKU)
    search_query = filters.get('search')
    if search_query:
        from django.db.models import Q
        qs = qs.filter(
            Q(name__icontains=search_query) | 
            Q(variants__sku__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        ).distinct()

    # 2. Category Filter
    category_id = filters.get('category')
    if category_id:
        qs = qs.filter(category_id=category_id)

    # 3. Brand Filter
    brand_id = filters.get('brand')
    if brand_id:
        qs = qs.filter(brand_id=brand_id)

    # 4. Price Range Filter
    min_price = filters.get('min_price')
    if min_price:
        qs = qs.filter(base_price__gte=min_price)
    
    max_price = filters.get('max_price')
    if max_price:
        qs = qs.filter(base_price__lte=max_price)

    # 5. Stock Status Filter
    stock_status = filters.get('stock_status')
    if stock_status == 'in_stock':
        qs = qs.filter(variants__stock_quantity__gt=0).distinct()
    elif stock_status == 'out_of_stock':
        # This is a bit trickier: products where ALL variants have 0 stock
        from django.db.models import Sum
        qs = qs.annotate(total_stock=Sum('variants__stock_quantity')).filter(total_stock=0)

    return qs

def get_product_by_slug(slug: str) -> Product:
    return Product.objects.filter(slug=slug, is_active=True).prefetch_related('variants', 'media').first()
