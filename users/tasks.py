from celery import shared_task
from django.utils import timezone

from users.models import User


@shared_task()
def block_inactive_users():
    """
    Блокирует пользователя, если он не заходил более месяца
    """
    today = timezone.now()

    users = User.objects.filter(is_active=True)
    for user in users:
        if user.last_login and (today - user.last_login).days >= 30:
            user.is_active = False
            user.save()
            print(f"{user} - заблокирован")
