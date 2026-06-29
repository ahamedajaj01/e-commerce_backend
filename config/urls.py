"""
URL Configuration for allinonenepal project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from apps.users.forms import EmailAdminAuthenticationForm

admin.site.login_form = EmailAdminAuthenticationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.v1.urls', namespace='api-v1')),
]

# Serve media and static files during development
# This allows you to open image links directly in the browser
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
