from django.contrib import admin

from .models import Course, Lesson, Payment


# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Класс для отображения модели Course в интерфейсе админки
    """

    list_display = ("id", "name")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """
    Класс для отображения модели Lesson в интерфейсе админки
    """

    list_display = ("id", "name")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Класс для отображения модели Payment в интерфейсе админки
    """

    list_display = ("id", "payment_date")
