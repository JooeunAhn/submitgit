"""submitgit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from allauth.account.views import confirm_email
from rest_framework import routers

from accounts.views import ProfileViewSet


router = routers.SimpleRouter()
router.register(r'profile', ProfileViewSet)


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.account.urls')),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/rest-auth/', include('rest_auth.urls')),
    url(r'^api/v1/rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$', confirm_email, name='account_confirm_email'),
    url(r'^api/v1/rest-auth/registration/', include('rest_auth.registration.urls')),
    # health checker for AWS EB
    url(r'^health$', include('health_check.urls')),
]
