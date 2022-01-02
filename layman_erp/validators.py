import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordCombinationValidator:
    def validate(self, password, user=None):
        if not re.findall(r'[\d]', password) \
                or not re.findall(r'[A-Z]', password) \
                or not re.findall(r'[a-z]', password) \
                or not re.findall(r'[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', password):
            raise ValidationError(
                _(
                    "Password must contain at least "
                    "1 digit, 1 uppercase letter, 1 lowercase letter, and 1 symbol."
                ),
                code='password_combination_error',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least "
            "1 digit, 1 uppercase letter, 1 lowercase letter, and 1 symbol."
        )
