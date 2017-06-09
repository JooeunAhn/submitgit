import re

from django.forms import ValidationError
from allauth.account.adapter import DefaultAccountAdapter


class HanyangEmailAdapter(DefaultAccountAdapter):
    def clean_email(self, email):
        if not re.match(r'[^@]+@hanyang\.ac\.kr', email):
            # TODO 왜 한양mail은 mail을 받지 못하는가?
            return email
            raise ValidationError("Plz use hanyang email")
        return email
