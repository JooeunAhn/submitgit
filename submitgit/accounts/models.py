from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name="profile")
    is_prof = models.BooleanField(default=False)
    name = models.CharField(max_length=20)
    sid = models.CharField(max_length=20, blank=True)
    github_username = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    @property
    def username(self):
        return self.user.username

    @property
    def email(self):
        return self.user.email
