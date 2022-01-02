from django.contrib.admin import AdminSite as DJAdminSite
from django.contrib.admin.forms import AdminAuthenticationForm
from django.forms import forms


class SuperUserAuthenticationForm(AdminAuthenticationForm):

    def confirm_login_allowed(self, user):
        """
        Locks out anyone but superusers.
        """
        super().confirm_login_allowed(user)

        if not user.is_superuser:
            raise forms.ValidationError(
                (
                    "Please enter the correct username and password for a superuser "
                    "account. Note that both fields may be case-sensitive."
                ),
                code='invalid_login',
            )


class AdminSite(DJAdminSite):
    # Customize Django Admin
    site_header = "Layman ERP Platform Admin"
    site_title = "Layman ERP Platform Admin"
    index_title = "Welcome to Layman ERP Platform Admin"
    login_form = SuperUserAuthenticationForm

    def register(self, model_or_iterable, admin_class=None, **options):
        from utils.admin import CustomModelAdmin  # pylint: disable=import-outside-toplevel
        admin_class = admin_class or CustomModelAdmin
        super().register(model_or_iterable, admin_class=admin_class, **options)
