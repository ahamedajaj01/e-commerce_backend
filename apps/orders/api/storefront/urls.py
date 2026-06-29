from django.urls import path
from .views import OrderListView, OrderDetailView, OrderTrackingView

app_name = 'storefront'

urlpatterns = [
    path('', OrderListView.as_view(), name='list'),
    path('track/', OrderTrackingView.as_view(), name='tracking'),
    path('<uuid:order_id>/', OrderDetailView.as_view(), name='detail'),
]
