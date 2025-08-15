from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    """
    Модель пользователей сервиса
    """

    email = models.EmailField(unique=True, verbose_name="Email")
    username = models.CharField(
        max_length=25, verbose_name="Ник пользователя", null=True, blank=True
    )

    phone_number = models.CharField(
        max_length=15, verbose_name="Телефон", null=True, blank=True
    )
    avatar = models.ImageField(
        upload_to="users/avatars/", verbose_name="Аватар", null=True, blank=True
    )
    country = models.CharField(
        max_length=100, verbose_name="Страна", null=True, blank=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
