from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    """
    Заполнение БД пользователями и группами
    """

    def handle(self, *args: list, **kwargs: dict) -> None:

        User.objects.all().delete()
        Group.objects.all().delete()

        call_command("loaddata", "groups.json")
        call_command("loaddata", "users.json")

        self.stdout.write(
            self.style.SUCCESS(
                "Фикстуры из файлов users.json и groups.json успешно загружены"
            )
        )
