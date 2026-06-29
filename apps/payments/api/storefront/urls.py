from django.urls import path
from .views import (
    ActivePaymentMethodsView, 
    PaymentTransactionInitView, 
    PaymentProofUploadView
)

app_name = 'storefront'

urlpatterns = [
    path('methods/', ActivePaymentMethodsView.as_view(), name='methods-list'),
    path('transactions/', PaymentTransactionInitView.as_view(), name='transaction-init'),
    path('transactions/<uuid:transaction_id>/proof/', PaymentProofUploadView.as_view(), name='proof-upload'),
]
