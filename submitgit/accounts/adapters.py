import re

from django.forms import ValidationError
from allauth.account.adapter import DefaultAccountAdapter


class HanyangEmailAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        if not re.match(r'[^@]+@hanyang\.ac\.kr', email):
            raise ValidationError("Plz use hanyang email")
        return email
