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

from .models import Profile, Test
from .serializers import ProfileSerializer, TestSerializer
from .permissions import IsOwnerOrReadOnly


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


# TODO update 구현하기 is owner
class ProfileViewSet(viewsets.GenericViewSet,
                     mixins.UpdateModelMixin,
                     mixins.CreateModelMixin):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def retrieve(self, request, pk=None):
        if pk != "me":
            return Response(status=status.HTTP_403_FORBIDDEN)

        if not hasattr(request.user, "profile"):
            return Response({})

        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        if pk != "me":
            return Response(status=status.HTTP_403_FORBIDDEN)
        partial = kwargs.pop('partial', False)
        instance = Profile.objects.get(user=request.user)
        serializer = self.get_serializer(instance,
                                         data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class TestViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
