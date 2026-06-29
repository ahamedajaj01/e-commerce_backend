from django.urls import path, include

app_name = 'payments'

urlpatterns = [
    # Storefront (Buyer)
    path('storefront/', include('apps.payments.api.storefront.urls', namespace='storefront')),
    
    # Backoffice (Admin)
    path('backoffice/', include('apps.payments.api.backoffice.urls', namespace='backoffice')),
]
