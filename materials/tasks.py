from celery import shared_task
from django.core.mail import send_mail

from conf import settings

from .models import Course, Subscription


@shared_task()
def send_message_about_course_update(pk):
    """
    Отправка подписавшимся пользователям уведомления об обновлении
    """
    course = Course.objects.get(pk=pk)
    message = f"Курс {course} обновлен"
    subscriptions = Subscription.objects.filter(course=course, is_active=True)

    if subscriptions.exists():
        users = [subscription.owner for subscription in subscriptions]
        users_emails = [user.email for user in users]
        send_mail("Новые материалы", message, settings.EMAIL_HOST_USER, users_emails)
