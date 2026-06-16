from django.db.models import QuerySet
from ..models import (
    AnnouncementBar, 
    NavigationMenu, 
    NavigationItem, 
    HomepageSection, 
    Promotion
)

def get_active_announcements() -> QuerySet:
    return AnnouncementBar.objects.filter(is_active=True).order_by('sort_order')

def get_active_navigation() -> QuerySet:
    from django.db.models import Prefetch
    
    # 1. Prepare items with their categories prefetched to avoid round-trips
    items_qs = NavigationItem.objects.filter(is_active=True).select_related('linked_category').order_by('sort_order')
    
    # 2. Fetch menus with all their items in ONE trip to Supabase
    return NavigationMenu.objects.filter(is_active=True).prefetch_related(
        Prefetch('items', queryset=items_qs)
    ).order_by('sort_order')

def get_navigation_items_for_menu(menu: NavigationMenu) -> QuerySet:
    # Get top-level items and prefetch children/categories in one hit
    return menu.items.filter(
        parent__isnull=True, 
        is_active=True
    ).select_related('linked_category').prefetch_related('children').order_by('sort_order')

def get_homepage_sections() -> QuerySet:
    return HomepageSection.objects.filter(is_active=True).order_by('sort_order')

def get_promotion_by_id(promo_id: str) -> Promotion:
    return Promotion.objects.filter(id=promo_id, is_active=True).first()

def get_active_promotions(filters: dict = None) -> QuerySet:
    qs = Promotion.objects.filter(is_active=True).prefetch_related(
        'products', 'products__variants', 'products__media'
    ).select_related('category', 'brand')
    
    if filters and filters.get('type'):
        qs = qs.filter(promotion_type=filters.get('type').upper())
    return qs.order_by('sort_order')
