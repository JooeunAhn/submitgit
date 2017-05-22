from datetime import datetime, timezone

from django.core.files.base import ContentFile
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, mixins, status
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Course, Repository, Assignment, Submission, EncryptedCode
from .serializers import CourseSerializer, CourseWithoutStudentsSerializer
from .serializers import RepositorySerializer, AssignmentSerializer
from .serializers import SubmissionSerializer, AssignmentCreateSerializer
from .serializers import EncryptedCodeSerializer
from .permissions import IsOwnerProfessorOrReadOnly
from .permissions import IsCourseOwnerProfessorOrReadOnly
from .utils import connect_queue

github_url = "https://raw.githubusercontent.com/"
lang_extension = {
    0: ".py",
    1: ".rb",
    2: ".clj",
    3: ".php",
    4: ".js",
    5: ".scala",
    6: ".go",
    7: ".c",
    8: ".java",
    9: ".vb",
    10: ".cs",
    11: ".sh",
    12: ".m",
    13: ".sql",
    14: ".pl",
    15: ".cpp"
}


def manual(request, pk):
    import requests as rq
    from requests.exceptions import RequestException
    now = datetime.now(timezone.utc)
    assignment = get_object_or_404(Assignment, pk=pk)

    if assignment.deadline < now:
        return HttpResponse("you can't submit the assignment")

    repo = Repository.objects.filter(course=assignment.course,
                                     student=request.user,
                                     is_verified=True).first()
    if not repo:
        return HttpResponse("you are not registered in this course")

    if Submission.objects.filter(student=request.user,
                                 assignment=assignment,
                                 is_working=True).exists():
        return HttpResponse("your assignment is on grading")

    repo_url = [i for i in repo.url.split('/') if i != ""]
    github_repo_name = repo_url.pop()
    github_username = repo_url.pop()

    code = ""
    langid = None

    for lang in assignment.test_langids.split(','):
        lang = int(lang)
        res = rq.get(
            github_url+"%s/%s/master/%s%s" % (github_username,
                                              github_repo_name,
                                              assignment.test_file_name,
                                              lang_extension[lang])
            )
        try:
            res.raise_for_status()
        except RequestException:
            continue
        code = res.text
        langid = lang
        if langid == 15:
            langid = 7

    if code is "":
        return HttpResponse("There isn't any code")

    f = ContentFile(code, name=assignment.test_file_name+lang_extension[lang])
    submission = Submission.objects.create(student=request.user,
                                           assignment=assignment,
                                           raw_code=f)
    queue_data = {'id': submission.pk, 'stdin': assignment.test_input,
                  'time': assignment.test_time, 'is_test': assignment.is_test,
                  'output': assignment.test_output, 'language': langid,
                  'code': code}
    connect_queue(queue_data)
    return HttpResponse("Submitted")


class CourseViewSet(viewsets.GenericViewSet,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = (IsAuthenticated, IsOwnerProfessorOrReadOnly)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        keyword = request.query_params.get("keyword", None)

        if keyword is not None:
            queryset = \
                queryset.filter(Q(title__contains=keyword) |
                                Q(professor__profile__name__contains=keyword))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CourseWithoutStudentsSerializer(page, many=True)
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
    serializer_class = AssignmentCreateSerializer
    permission_classes = (IsAuthenticated, IsCourseOwnerProfessorOrReadOnly)

    def create(self, request, *args, **kwargs):
        if not request.user.profile.is_prof:
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
        data['attachments'] = instance.attachments.url \
            if instance.attachments else None
        data['course'] = instance.course.pk
        data['deadline'] = instance.deadline
        data['is_test'] = instance.is_test
        data['test_file_name'] = instance.test_file_name
        data['test_langids'] = instance.test_langids
        data['created_at'] = instance.created_at
        data['updated_at'] = instance.updated_at
        data['submission_set'] = submission_data
        return Response(data)

    @list_route(methods=['get'])
    def me(self, request, *args, **kwargs):

        if request.user.profile.is_prof:
            return Response("Professors are not allowed",
                            status=status.HTTP_401_UNAUTHORIZED)

        now = datetime.now(timezone.utc)
        repo_list = Repository.objects.filter(student=request.user,
                                              is_verified=True)
        course_list = Course.objects.filter(repository__in=repo_list)
        assignment_list = Assignment.objects.filter(course__in=course_list,
                                                    deadline__gte=now)

        page = self.paginate_queryset(assignment_list)
        if page is not None:
            serializer = AssignmentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AssignmentSerializer(assignment_list, many=True)
        return Response(serializer.data)


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = (IsAdminUser,)


class EncryptedCodeViewSet(viewsets.GenericViewSet,
                           mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin):
    queryset = EncryptedCode.objects.all()
    serializer_class = EncryptedCodeSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        assignment = Assignment.objects.filter(
            pk=request.data['assignment']).first()
        if assignment is None or \
           not Repository.objects.filter(student=request.user,
                                         course=assignment.course,
                                         is_verified=True).exists():
            return Response("You are not registered",
                            status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        data['student'] = request.user.pk
        # TODO: Encrypting
        # return: <class 'django.core.files.uploadedfile.InMemoryUploadedFile'>
        # return ext: .tar
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)
