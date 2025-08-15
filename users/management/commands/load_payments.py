from django.core.management import call_command
from django.core.management.base import BaseCommand

from users.models import Payment


class Command(BaseCommand):
    """
    Заполнение БД фикстурой платежей сервиса
    """

    def handle(self, *args: list, **kwargs: dict) -> None:

        Payment.objects.all().delete()

        call_command("loaddata", "payments.json")

        self.stdout.write(
            self.style.SUCCESS("Фикстуры из файла payments.json успешно загружены")
        )
