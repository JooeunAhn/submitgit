from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import SocialLoginView
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Profile
from .serializers import ProfileSerializer


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
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(request.user.profile)
        return Response(serializer.data)
