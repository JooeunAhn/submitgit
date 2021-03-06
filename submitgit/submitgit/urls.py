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
from django.views.generic import TemplateView

from allauth.account.views import confirm_email
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from accounts.views import ProfileViewSet
from portal.views import CourseViewSet, RepositoryViewSet, AssignmentViewSet
from portal.views import SubmissionViewSet, EncryptedCodeViewSet, manual
from portal.views import download_zip

schema_view = get_swagger_view(title="submitgit API")

router = routers.SimpleRouter()
router.register(r'profile', ProfileViewSet)

router.register('course', CourseViewSet)
router.register('repo', RepositoryViewSet)
router.register('assignment', AssignmentViewSet)
router.register('submission', SubmissionViewSet)
router.register('encryptor', EncryptedCodeViewSet)


urlpatterns = [
    url(r'^schema$', schema_view),
    url(r'^$', TemplateView.as_view(template_name="angular/index.html"), name="index"),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.account.urls')),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/rest-auth/', include('rest_auth.urls')),
    url(r'^api/v1/rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$', confirm_email, name='account_confirm_email'),
    url(r'^api/v1/rest-auth/registration/', include('rest_auth.registration.urls')),
    # health checker for AWS EB
    url(r'^health$', include('health_check.urls')),
    url(r'manual/(?P<pk>\d+)/$', manual, name="manual"),
    url(r'download_zip/(?P<pk>\d+)/$', download_zip, name="download_zip"),
]
