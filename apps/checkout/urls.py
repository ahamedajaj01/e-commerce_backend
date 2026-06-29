from django.urls import path, include

app_name = 'checkout'

urlpatterns = [
    # Storefront (Buyer)
    path('storefront/', include('apps.checkout.api.storefront.urls', namespace='storefront')),
    
    # Backoffice (Admin)
    path('backoffice/', include('apps.checkout.api.backoffice.urls', namespace='backoffice')),
]
