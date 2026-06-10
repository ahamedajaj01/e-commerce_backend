from django.urls import path
from .catalog_views import AdminProductView, AdminProductDetailView, AdminCategoryView, AdminCategoryDetailView
from .inventory_views import AdminInventoryView, AdminInventoryAdjustmentView, AdminLowStockView
from .cms_views import (
    AdminAnnouncementView,
    AdminAnnouncementDetailView,
    AdminNavigationMenuView,
    AdminNavigationMenuDetailView,
    AdminNavigationItemView,
    AdminNavigationItemDetailView,
    AdminHomepageSectionView,
    AdminHomepageSectionDetailView,

    AdminPromotionView,
    AdminPromotionDetailView
)

from .shipping_views import AdminShippingRuleListView, AdminShippingRuleDetailView, AdminShippingRuleToggleView

app_name = 'backoffice'

urlpatterns = [
    # Products
    path('products/', AdminProductView.as_view(), name='admin-product-list'),
    path('products/<uuid:product_id>/', AdminProductDetailView.as_view(), name='admin-product-detail'),

    # Categories
    path('categories/', AdminCategoryView.as_view(), name='admin-category-list'),
    path('categories/<int:category_id>/', AdminCategoryDetailView.as_view(), name='admin-category-detail'),

    # Inventory
    path('inventory/', AdminInventoryView.as_view(), name='admin-inventory-list'),
    path('inventory/adjust/', AdminInventoryAdjustmentView.as_view(), name='admin-inventory-adjust'),
    path('inventory/low-stock/', AdminLowStockView.as_view(), name='admin-low-stock'),

    # CMS
    path('cms/announcements/', AdminAnnouncementView.as_view(), name='admin-announcement-list'),
    path('cms/announcements/<uuid:pk>/', AdminAnnouncementDetailView.as_view(), name='admin-announcement-detail'),
    path('cms/navigation/', AdminNavigationMenuView.as_view(), name='admin-navigation-list'),
    path('cms/navigation/<uuid:pk>/', AdminNavigationMenuDetailView.as_view(), name='admin-navigation-detail'),
    path('cms/navigation-items/', AdminNavigationItemView.as_view(), name='admin-navigation-item-create'),
    path('cms/navigation-items/<uuid:pk>/', AdminNavigationItemDetailView.as_view(), name='admin-navigation-item-detail'),
    path('cms/homepage-sections/', AdminHomepageSectionView.as_view(), name='admin-homepage-section-list'),
    path('cms/homepage-sections/<uuid:pk>/', AdminHomepageSectionDetailView.as_view(), name='admin-homepage-section-detail'),

    path('cms/promotions/', AdminPromotionView.as_view(), name='admin-promotion-list'),
    path('cms/promotions/<uuid:pk>/', AdminPromotionDetailView.as_view(), name='admin-promotion-detail'),

    # Shipping
    path('shipping/rules/', AdminShippingRuleListView.as_view(), name='admin-shipping-rule-list'),
    path('shipping/rules/<uuid:pk>/', AdminShippingRuleDetailView.as_view(), name='admin-shipping-rule-detail'),
    path('shipping/rules/<uuid:pk>/toggle/', AdminShippingRuleToggleView.as_view(), name='admin-shipping-rule-toggle'),
]
