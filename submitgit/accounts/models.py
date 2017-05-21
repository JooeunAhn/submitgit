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


class Test(models.Model):
    LANG_CHOICES = (
        (0, "Python"),
        (1, "Ruby"),
        (2, "Clojure"),
        (3, "PHP"),
        (4, "Javascript"),
        (5, "Scala"),
        (6, "Go"),
        (7, "C,C++"),
        (8, "Java"),
        (9, "VB.NET"),
        (10, "C#"),
        (11, "Bash"),
        (12, "Objective-C"),
        (13, "MySQL"),
        (14, "Perl"),
    )
    langid = models.IntegerField(choices=LANG_CHOICES)
    code = models.TextField(max_length=5000)
    errors = models.TextField(max_length=1000, blank=True)
    output = models.TextField(max_length=5000, blank=True)
    time = models.FloatField()
