from django.contrib.auth.models import Group
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAdminUser

from src.utils import get_queryset_for_owner
from users.permissions import IsModerator, IsOwner

from .models import Course, Lesson, Subscription
from .paginators import CoursePaginator, LessonPaginator
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    StaffCourseSerializer,
    SubscriptionSerializer,
)
from .tasks import send_message_about_course_update


# Create your views here.
class CourseViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для CRUD операций с моделью Course
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_permissions(self):
        """
        Выдача разрешений в зависимости от статуса пользователя
        """
        if self.action == "create":
            self.permission_classes = [~IsModerator]
        elif self.action in ["update", "retrieve"]:
            self.permission_classes = [IsOwner | IsModerator | IsAdminUser]
        elif self.action == "destroy":
            self.permission_classes = [IsOwner | IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        """
        Подбор списка объектов в зависимости от статуса пользователя
        """
        return get_queryset_for_owner(self.request.user, self.queryset)

    def perform_create(self, serializer):
        """
        Сохранение владельца при создании объекта
        """
        course = serializer.save()
        course.owner = self.request.user
        course.save()

    def perform_update(self, serializer):
        """
        Отправка подписавшимся пользователям уведомления об обновлении курса
        """
        previous_update_date = self.get_object().updated_at
        course = serializer.save()
        current_update_date = course.updated_at
        if (current_update_date - previous_update_date).seconds >= 4 * 60 * 60:
            send_message_about_course_update.delay(course.pk)

    def get_serializer_class(self):
        """
        Подбор сериализатора в зависимости от статуса пользователя
        """
        try:
            if self.request.user.is_superuser or self.request.user.groups.get(
                name="Moderators"
            ):
                return StaffCourseSerializer
        except Group.DoesNotExist:
            return CourseSerializer


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    Дженерик для отображения списка и создания нового объекта Lesson:
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_permissions(self):
        """
        Выдача разрешений в зависимости от статуса пользователя
        """
        if self.request.method == "POST":
            self.permission_classes = [~IsModerator]
        return super().get_permissions()

    def get_queryset(self):
        """
        Подбор списка объектов в зависимости от статуса пользователя
        """
        return get_queryset_for_owner(self.request.user, self.queryset)

    def perform_create(self, serializer):
        """
        Сохранение владельца при создании объекта и отправка уведомления подписанным пользователям об изменении курса
        """
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()

        course = lesson.course
        if course:
            previous_update_date = course.updated_at
            current_update_date = lesson.updated_at
            if (current_update_date - previous_update_date).seconds >= 4 * 60 * 60:
                send_message_about_course_update.delay(course.pk)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Дженерик для просмотра, редактирования и удаления объекта Lesson:
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        """
        Выдача разрешений в зависимости от статуса пользователя
        """
        if self.request.method in ["PATCH", "PUT", "GET"]:
            self.permission_classes = [IsOwner | IsModerator | IsAdminUser]
        elif self.request.method == "DELETE":
            self.permission_classes = [IsOwner | IsAdminUser]
        return super().get_permissions()

    def perform_update(self, serializer):
        """
        Отправка уведомления подписанным пользователям об изменении курса
        """
        lesson = serializer.save()

        course = lesson.course
        if course:
            previous_update_date = course.updated_at
            current_update_date = lesson.updated_at
            if (current_update_date - previous_update_date).seconds >= 4 * 60 * 60:
                send_message_about_course_update.delay(course.pk)


class SubscriptionListCreateAPIView(generics.ListCreateAPIView):
    """
    Дженерик для отображения списка и создания нового объекта Subscription:
    """

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        """
        Выдача разрешений в зависимости от статуса пользователя
        """
        if self.request.method == "POST":
            self.permission_classes = [IsModerator | IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        """
        Подбор списка объектов в зависимости от статуса пользователя
        """
        return get_queryset_for_owner(self.request.user, self.queryset)


class SubscriptionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Дженерик для просмотра, редактирования и удаления объекта Subscription:
    """

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

    def get_permissions(self):
        """
        Выдача разрешений в зависимости от статуса пользователя
        """
        if self.request.method == "GET":
            self.permission_classes = [IsOwner | IsModerator | IsAdminUser]
        elif self.request.method in ["PATCH", "PUT", "DELETE"]:
            self.permission_classes = [IsModerator | IsAdminUser]
        return super().get_permissions()
