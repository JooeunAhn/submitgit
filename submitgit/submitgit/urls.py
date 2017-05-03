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
from accounts.views import GitHubLogin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.account.urls')),
    url(r'^rest-auth/github/$', GitHubLogin.as_view(), name='github_login'),
    url(r'^rest-auth/registration/account-confirm-email/(?P<key>\w+)/$',confirm_email, name='account_confirm_email'),
    # health checker for AWS EB
    url(r'^health/$', include('health_check.urls')),
]
