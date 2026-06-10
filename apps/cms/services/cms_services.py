from django.db import transaction
from ..models import (
    AnnouncementBar,
    NavigationMenu,
    NavigationItem,
    HomepageSection
)

@transaction.atomic
def create_navigation_menu(*, title: str, slug: str, is_active: bool = True) -> NavigationMenu:
    return NavigationMenu.objects.create(title=title, slug=slug, is_active=is_active)

@transaction.atomic
def create_navigation_item(*, menu: NavigationMenu, title: str, parent=None, linked_category=None, linked_url: str = "", sort_order: int = 0) -> NavigationItem:
    return NavigationItem.objects.create(
        menu=menu,
        title=title,
        parent=parent,
        linked_category=linked_category,
        linked_url=linked_url,
        sort_order=sort_order
    )

@transaction.atomic
def toggle_announcement(*, announcement_id: str) -> bool:
    announcement = AnnouncementBar.objects.get(pk=announcement_id)
    announcement.is_active = not announcement.is_active
    announcement.save()
    return announcement.is_active

@transaction.atomic
def update_navigation_order(*, item_id: str, sort_order: int) -> None:
    NavigationItem.objects.filter(pk=item_id).update(sort_order=sort_order)

@transaction.atomic
def toggle_homepage_section(*, section_id: str) -> bool:
    section = HomepageSection.objects.get(pk=section_id)
    section.is_active = not section.is_active
    section.save()
    return section.is_active
