from rest_framework import viewsets, mixins, status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Course, Repository
from .serializers import CourseSerializer, CourseWithoutStudentsSerializer
from .serializers import RepositorySerializer


class IsOwnerProfessorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.professor == request.user


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
            return Response(None, status=status.HTTP_403_FORBIDDEN)
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

    def create(self, request, *args, **kwargs):
        if request.user.profile.is_prof:
            return Response(None, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if Repository.objects.filter(course=request.data['course'],
                                     student=request.user).exists():
            return Response(None, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(None, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance,
                                         data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def perform_update(self, serializer):
        if self.requser.user.profile.is_prof:
            return serializer.save()
        return serializer.save(student=self.requser.user, is_verified=False)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not (instance.student == request.user or
                instance.course.professor == request.user):
            return Response(None, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
