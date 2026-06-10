from django.urls import path, include

app_name = 'auth'

urlpatterns = [
    # Include authentication app urls
    path('', include('apps.authentication.api.urls', namespace='authentication')),
]
