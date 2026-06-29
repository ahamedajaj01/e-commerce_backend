from django.urls import path
from .views import (
    CheckoutSessionCreateView, 
    CheckoutSessionDetailView, 
    CheckoutSessionCompleteView
)

app_name = 'storefront'

urlpatterns = [
    path('sessions/', CheckoutSessionCreateView.as_view(), name='session-create'),
    path('sessions/<uuid:session_id>/', CheckoutSessionDetailView.as_view(), name='session-detail'),
    path('sessions/<uuid:session_id>/complete/', CheckoutSessionCompleteView.as_view(), name='session-complete'),
]
