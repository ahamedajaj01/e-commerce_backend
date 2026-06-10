from django.contrib.admin.forms import AdminAuthenticationForm
from django import forms
from django.utils.translation import gettext_lazy as _

class EmailAdminAuthenticationForm(AdminAuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'autofocus': True}),
        label=_("Email address")
    )
    
    error_messages = {
        'invalid_login': _(
            "Please enter a correct %(username)s and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        self.error_messages['invalid_login'] = _(
            "Please enter a correct email address and password. Note that both "
            "fields may be case-sensitive."
        )
