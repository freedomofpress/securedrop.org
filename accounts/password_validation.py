from django.core.exceptions import ValidationError
from zxcvbn import zxcvbn


class ZxcvbnValidator(object):
    def validate(self, password, user=None):
        user_inputs = []
        if user:
            user_inputs = [
                user.email,
                user.username,
                user.first_name,
                user.last_name,
            ]
        result = zxcvbn(password, user_inputs=user_inputs)
        if result['score'] < 4:
            warning = result['feedback']['warning']
            suggestions = result['feedback']['suggestions']
            messages = [warning] + suggestions if warning else suggestions
            if not messages:
                messages = 'Use a stronger password.'
            raise ValidationError(messages)
