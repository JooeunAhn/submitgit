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


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ("id", "student", "assignment", "is_passed", "has_error",
                  "raw_code", "code", "langid", "errors", "output", "time",
                  "created_at", "updated_at")


class AssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment
        fields = (
            "id", "title", "content", "attachments", 'course', "deadline",
            "is_test", "test_file_name", "test_input", "test_output",
            "created_at", "updated_at")


class CourseSerializer(serializers.ModelSerializer):
    professor = UserSerializer(required=False)
    repository_set = RepositorySerializer(read_only=True, many=True)
    attachments = serializers.FileField(required=False, allow_empty_file=True)
    assignment_set = AssignmentSerializer(read_only=True, many=True)

    class Meta:
        model = Course
        fields = (
            'id', 'professor', 'repository_set', 'title', "assignment_set",
            'content', 'year', 'semester', 'full_semester',
            'attachments', 'created_at', 'updated_at')


class CourseWithoutStudentsSerializer(serializers.ModelSerializer):
    professor = UserSerializer(read_only=True)
    assignment_set = AssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ("id", "professor", "title", "content",
                  "year", "semester", "attachments", "assignment_set",
                  "created_at", "updated_at", 'full_semester')
