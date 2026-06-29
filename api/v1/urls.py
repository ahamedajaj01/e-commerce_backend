from django.urls import path, include

app_name = 'v1'

urlpatterns = [
    # Auth
    path('auth/', include('apps.authentication.api.urls', namespace='auth')),
    
    # Storefront (Discovery, Cart, Shipping, Orders)
    path('storefront/', include('api.v1.storefront.urls', namespace='storefront')),
    
    # Checkout (Orchestration)
    path('checkout/', include('apps.checkout.urls', namespace='checkout')),
    
    # Payments (Transactions & Proofs)
    path('payments/', include('apps.payments.urls', namespace='payments')),
    
    # Backoffice (Admin Panel)
    path('backoffice/', include('api.v1.backoffice.urls', namespace='backoffice')),
]
