from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from .apps import MaterialsConfig

app_name = MaterialsConfig.name

router = DefaultRouter()
router.register("courses", views.CourseViewSet, basename="courses")

urlpatterns = [
    path("lessons/", views.LessonListCreateAPIView.as_view(), name="lessons"),
    path(
        "lessons/<int:pk>/",
        views.LessonRetrieveUpdateDestroyAPIView.as_view(),
        name="lesson",
    ),
    path(
        "subscriptions/",
        views.SubscriptionListCreateAPIView.as_view(),
        name="subscriptions",
    ),
    path(
        "subscriptions/<int:pk>/",
        views.SubscriptionRetrieveUpdateDestroyAPIView.as_view(),
        name="subscription",
    ),
] + router.urls
