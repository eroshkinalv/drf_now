from django.core.management import call_command
from django.core.management.base import BaseCommand

from mypedia.models import Course, Lesson, Payment, Subscription


class Command(BaseCommand):
    """
    Заполнение БД фикстурами курсов, уроков и платежей сервиса
    """

    def handle(self, *args: list, **kwargs: dict) -> None:

        Payment.objects.all().delete()
        Subscription.objects.all().delete()
        Lesson.objects.all().delete()
        Course.objects.all().delete()

        call_command("loaddata", "mypedia.json")
        call_command("loaddata", "payments.json")

        self.stdout.write(
            self.style.SUCCESS(
                "Фикстуры из файлов mypedia.json и payments.json успешно загружены"
            )
        )
