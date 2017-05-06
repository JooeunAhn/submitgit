from django.contrib.auth.models import User
from django.dispatch import receiver

from allauth.account.models import EmailAddress
from allauth.account.signals import user_signed_up, email_confirmed
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import SocialLoginView
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Profile
from .serializers import ProfileSerializer


@receiver(user_signed_up)
def _user_signed_up(request, user, **kwargs):
    user.is_active = False
    user.save()


@receiver(email_confirmed)
def _email_confirmed(request, email_address, **kwargs):
    email = EmailAddress.objects.get(email=email_address)
    user = User.objects.get(email.user)
    user.is_active = True
    user.save()


class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    client_class = OAuth2Client


class ProfileViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk=None):
        if pk != "me":
            return Response(status=status.HTTP_403_FORBIDDEN)

        if not hasattr(request.user, "profile"):
            return Response({})

        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)
