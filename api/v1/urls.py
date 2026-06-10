"""
API v1 URL Configuration for allinonenepal project.
"""

from django.urls import path, include

app_name = 'api-v1'

urlpatterns = [
    path('auth/', include('api.v1.auth.urls', namespace='auth')),
    path('storefront/', include('api.v1.storefront.urls', namespace='storefront')),
    path('backoffice/', include('api.v1.backoffice.urls', namespace='backoffice')),
    path('system/', include('api.v1.system.urls', namespace='system')),
]
