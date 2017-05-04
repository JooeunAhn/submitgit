from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name="profile")
    is_prof = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    @property
    def username(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email
