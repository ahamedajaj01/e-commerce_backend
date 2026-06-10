from django.contrib import admin
from .models import (
    AnnouncementBar,
    NavigationMenu,
    NavigationItem,
    HomepageSection,
    Banner
)

@admin.register(AnnouncementBar)
class AnnouncementBarAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')

class NavigationItemInline(admin.TabularInline):
    model = NavigationItem
    extra = 1
    fk_name = 'parent'

@admin.register(NavigationMenu)
class NavigationMenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')

@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'menu', 'parent', 'linked_category', 'is_active', 'sort_order')
    list_filter = ('menu', 'is_active')
    list_editable = ('is_active', 'sort_order')

class BannerInline(admin.TabularInline):
    model = Banner
    extra = 1

@admin.register(HomepageSection)
class HomepageSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'section_type', 'is_active', 'sort_order')
    list_editable = ('is_active', 'sort_order')
    inlines = [BannerInline]

