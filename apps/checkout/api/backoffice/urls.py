from django.urls import path
from .views import AdminCheckoutSessionListView, AdminCheckoutSessionDetailView

app_name = 'backoffice'

urlpatterns = [
    path('sessions/', AdminCheckoutSessionListView.as_view(), name='session-list'),
    path('sessions/<uuid:session_id>/', AdminCheckoutSessionDetailView.as_view(), name='session-detail'),
]
