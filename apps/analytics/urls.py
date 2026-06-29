from django.urls import path, include

urlpatterns = [
    path('backoffice/', include('apps.analytics.api.backoffice.urls')),
]
