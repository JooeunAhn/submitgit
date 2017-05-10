from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Course, Repository, Assignment, Submission
from accounts.models import Profile


User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'username', 'email', 'name', 'sid')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'profile',)


class RepositorySerializer(serializers.ModelSerializer):
    student = UserSerializer(required=False)
    is_verified = serializers.BooleanField(required=False)

    class Meta:
        model = Repository
        fields = ('id', 'is_verified', 'student', 'course',
                  'url', 'created_at', 'updated_at')
        write_only_fields = ('course')


class CourseSerializer(serializers.ModelSerializer):
    professor = UserSerializer(required=False)
    repository_set = RepositorySerializer(read_only=True, many=True)
    attachments = serializers.FileField(required=False, allow_empty_file=True)

    class Meta:
        model = Course
        fields = (
            'id', 'professor', 'repository_set', 'title',
            'content', 'year', 'semester',
            'attachments', 'created_at', 'updated_at')


class CourseWithoutStudentsSerializer(serializers.ModelSerializer):
    professor = UserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ("id", "professor", "title", "content",
                  "year", "semester", "attachments",
                  "created_at", "updated_at",)
