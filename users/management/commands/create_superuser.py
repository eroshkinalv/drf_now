from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Создание администратора
    """

    def handle(self, *args, **options):

        User = get_user_model()
        user = User.objects.create(
            email=options["email"],
            first_name=options["first_name"],
            last_name=options["last_name"],
        )

        user.set_password("12345")
        user.is_staff = True
        user.is_superuser = True

        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Пользователь {user.email} с правами администратора успешно создан"
            )
        )

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, action="store", help="email")
        parser.add_argument("first_name", type=str, action="store", help="first_name")
        parser.add_argument("last_name", type=str, action="store", help="last_name")
