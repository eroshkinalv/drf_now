from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin

from .models import User


# Register your models here.
@register(User)
class CustomUserAdmin(UserAdmin):
    """
    Класс для отображения модели User в интерфейсе админки
    """

    list_display = ("id", "email", "username", "phone_number")
