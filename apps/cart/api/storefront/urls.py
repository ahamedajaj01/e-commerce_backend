from django.urls import path
from .views import CartDetailView, CartItemAddView, CartItemDetailView

app_name = 'cart'

urlpatterns = [
    path('', CartDetailView.as_view(), name='detail'),
    path('items/', CartItemAddView.as_view(), name='add'),
    path('items/<uuid:item_id>/', CartItemDetailView.as_view(), name='item-detail'),
]
