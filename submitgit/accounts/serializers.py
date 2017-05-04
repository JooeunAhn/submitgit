from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Profile
        fields = ('user', 'is_prof', 'username', 'email')
