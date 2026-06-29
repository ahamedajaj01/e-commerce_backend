from django.urls import path, include
from .catalog_views import ProductListView, CategoryListView, ProductDetailView
from .cms_views import (
    AnnouncementListView,
    NavigationListView,
    HomepageView,
    PromotionListView,
    PromotionDetailView
)

from .shipping_views import ShippingFeeCalculationView

app_name = 'storefront'

urlpatterns = [
    # Catalog
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    
    # CMS / Content
    path('announcements/', AnnouncementListView.as_view(), name='announcement-list'),
    path('navigation/', NavigationListView.as_view(), name='navigation-list'),
    path('homepage/', HomepageView.as_view(), name='homepage-layout'),
    path('promotions/', PromotionListView.as_view(), name='promotion-list'),
    path('promotions/<uuid:pk>/', PromotionDetailView.as_view(), name='promotion-detail'),
    
    # Cart
    path('cart/', include('apps.cart.api.storefront.urls', namespace='cart')),

    # Payments
    path('payments/', include('apps.payments.api.storefront.urls', namespace='payments-storefront')),

    # Shipping
    path('shipping/calculate/', ShippingFeeCalculationView.as_view(), name='shipping-calculate'),
    path('shipping/calculate', ShippingFeeCalculationView.as_view()),

    # Orders
    path('orders/', include('apps.orders.api.storefront.urls', namespace='orders')),
]
