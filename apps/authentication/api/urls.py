from django.urls import path
from .signup_views import SendOTPView, VerifyOTPView, CompleteSignupView
from .login_views import LoginView, MeView
from .password_views import (
    ChangePasswordView,
    ForgotPasswordView,
    VerifyResetOTPView,
    ResetPasswordView
)

app_name = 'authentication'

urlpatterns = [
    path('signup/send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('signup/verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('signup/complete/', CompleteSignupView.as_view(), name='complete-signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/me/', MeView.as_view(), name='me'), # Supporting standard auth paths
    path('profile/', MeView.as_view(), name='profile'),

    # Password Management
    path('password/change/', ChangePasswordView.as_view(), name='change-password'),
    path('password/forgot/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('password/verify-otp/', VerifyResetOTPView.as_view(), name='verify-reset-otp'),
    path('password/reset/', ResetPasswordView.as_view(), name='reset-password'),
]
