from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re

class CustomPasswordValidator:
    """
    Validates that a password:
    - Has at least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one number
    - Is alphanumeric
    """

    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(_("Password must be at least 8 characters long."))

        if not any(char.isdigit() for char in password):
            raise ValidationError(_("Password must contain at least one digit."))

        if not any(char.isupper() for char in password):
            raise ValidationError(_("Password must contain at least one uppercase letter."))

        if not re.search(r'[A-Za-z0-9]', password):
            raise ValidationError(_("Password must be alphanumeric."))

    def get_help_text(self):
        return _("Your password must be at least 8 characters long, contain a digit, an uppercase letter, and be alphanumeric.")
