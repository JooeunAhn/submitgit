"""
WSGI config for submitgit project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

settings_mode = "submitgit.settings.%s" % os.getenv("SETTINGS_MODE")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_mode)

application = get_wsgi_application()
