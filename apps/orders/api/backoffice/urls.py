from django.urls import path
from .views import AdminOrderListView, AdminOrderDetailView

app_name = 'backoffice'

urlpatterns = [
    path('', AdminOrderListView.as_view(), name='list'),
    path('<uuid:order_id>/', AdminOrderDetailView.as_view(), name='detail'),
]
