from django.core.management import call_command
from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    """
    Заполнение БД пользователями, группами и разрешениями
    """

    def handle(self, *args: list, **kwargs: dict) -> None:

        User.objects.all().delete()
        call_command("loaddata", "users.json")

        self.stdout.write(
            self.style.SUCCESS("Фикстуры из файла users.json успешно загружены")
        )
