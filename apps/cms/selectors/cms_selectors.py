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
    return NavigationMenu.objects.filter(is_active=True).order_by('sort_order')

def get_navigation_items_for_menu(menu: NavigationMenu) -> QuerySet:
    return NavigationItem.objects.filter(
        menu=menu, 
        parent__isnull=True, 
        is_active=True
    ).prefetch_related('children', 'category').order_by('sort_order')

def get_homepage_sections() -> QuerySet:
    return HomepageSection.objects.filter(is_active=True).order_by('sort_order')

def get_promotion_by_id(promo_id: str) -> Promotion:
    return Promotion.objects.filter(id=promo_id, is_active=True).first()

def get_active_promotions(filters: dict = None) -> QuerySet:
    qs = Promotion.objects.filter(is_active=True)
    if filters and filters.get('type'):
        qs = qs.filter(promotion_type=filters.get('type').upper())
    return qs.order_by('sort_order')
