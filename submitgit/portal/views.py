from rest_framework import viewsets, mixins, status
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Course, Repository, Assignment, Submission
from .serializers import CourseSerializer, CourseWithoutStudentsSerializer
from .serializers import RepositorySerializer, AssignmentSerializer
from .serializers import SubmissionSerializer
from .permissions import IsOwnerProfessorOrReadOnly
from .permissions import IsCourseOwnerProfessorOrReadOnly


class CourseViewSet(viewsets.GenericViewSet,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated, IsOwnerProfessorOrReadOnly)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CourseWithoutStudentsSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user == instance.professor:
            serializer = self.get_serializer(instance)
        else:
            serializer = CourseWithoutStudentsSerializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if not request.user.profile.is_prof:
            return Response("Prof Only", status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        return serializer.save(professor=self.request.user)


class RepositoryViewSet(viewsets.GenericViewSet,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin):

    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
    permission_classes = (IsAuthenticated,)

    @list_route(methods=['get'])
    def course(self, request):
        course_id = request.query_params.get('course_id')
        course = Course.objects.get(pk=course_id)
        repo = Repository.objects.get(course=course, student=request.user)
        serializer = self.get_serializer(repo)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if request.user.profile.is_prof:
            return Response("Student Only", status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Repository.objects.filter(course=request.data['course'],
                                     student=request.user).exists():
            return Response("Registraon Already Exists",
                            status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        return serializer.save(student=self.request.user, is_verified=False)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if not (instance.student == request.user or
                instance.course.professor == request.user):
            return Response("It is not yours",
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance,
                                         data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def perform_update(self, serializer):
        if self.request.user.profile.is_prof:
            return serializer.save()
        return serializer.save(student=self.requser.user, is_verified=False)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (instance.student == request.user or
                instance.course.professor == request.user):
            return Response("It is not yours",
                            status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignmentViewSet(viewsets.GenericViewSet,
                        mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.UpdateModelMixin):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer
    permission_classes = (IsAuthenticated, IsCourseOwnerProfessorOrReadOnly)

    def create(self, request, *args, **kwargs):
        if request.user.profile.is_prof:
            return Response("Prof Only", status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        prof = Course.objects.get(pk=request.data['course']).professor
        if prof != request.user:
            return Response("The course in request.data is not yours",
                            status=status.HTTP_403_FORBIDDEN)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def retrieve(self, request, pk):
        prof = Assignment.objects.get(pk=pk).course.professor
        instance = self.get_object()
        submission_set = instance.submission_set.filter(
            is_last_submission=True)
        prof = instance.course.professor
        if request.user in instance.course.students.all():
            submission_set = submission_set.filter(student=request.user) \
                .distinct()
        elif request.user == prof:
            pass
        else:
            return Response("it's not yours",
                            status=status.HTTP_401_UNAUTHORIZED)
        submission_data = SubmissionSerializer(submission_set,
                                               many=True).data

        data = {}

        if request.user == prof:
            data['test_input'] = instance.test_input
            data['test_output'] = instance.test_output

        data['id'] = instance.pk
        data['title'] = instance.title
        data['content'] = instance.content
        data['attachments'] = instance.attachments.url
        data['course'] = instance.course.pk
        data['deadline'] = instance.deadline
        data['is_test'] = instance.is_test
        data['test_file_name'] = instance.test_file_name
        data['test_langids'] = instance.test_langids
        data['created_at'] = instance.created_at
        data['updated_at'] = instance.updated_at
        data['submission_set'] = submission_data
        return Response(data)


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = (IsAdminUser,)
