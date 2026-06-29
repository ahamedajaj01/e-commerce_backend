from django.urls import path
from .views import (
    AdminTransactionListView, 
    AdminTransactionDetailView,
    AdminTransactionVerifyView,
    AdminPaymentMethodView,
    AdminPaymentMethodDetailView,
    AdminPaymentProviderView
)

app_name = 'backoffice'

urlpatterns = [
    # Providers (Technical Engines)
    path('providers/', AdminPaymentProviderView.as_view(), name='provider-list'),

    # Payment Methods Management
    path('methods/', AdminPaymentMethodView.as_view(), name='method-list'),
    path('methods/<uuid:pk>/', AdminPaymentMethodDetailView.as_view(), name='method-detail'),

    # Transactions & Verification
    path('transactions/', AdminTransactionListView.as_view(), name='transaction-list'),
    path('transactions/<uuid:transaction_id>/', AdminTransactionDetailView.as_view(), name='transaction-detail'),
    path('transactions/<uuid:transaction_id>/verify/', AdminTransactionVerifyView.as_view(), name='transaction-verify'),
]
