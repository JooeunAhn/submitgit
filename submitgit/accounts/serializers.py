from rest_framework import serializers

from .models import Profile, Test


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Profile
        fields = ('user', 'is_prof', 'username', 'email')


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ('langid', 'code', 'errors', 'time', 'output')
