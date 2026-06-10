from django.contrib import admin
from .models.otp import OTP
from .models.pending_registration import PendingRegistration

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('destination', 'code', 'purpose', 'expires_at', 'is_used')
    list_filter = ('purpose', 'is_used')
    search_fields = ('destination',)

@admin.register(PendingRegistration)
class PendingRegistrationAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_verified', 'created_at')
    readonly_fields = ('verification_token', 'created_at')
