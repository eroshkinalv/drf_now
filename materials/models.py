from django.contrib.auth import get_user_model
from django.db import models

PAYMENT_METHODS = [("cash", "Наличные"), ("transfer_to_account", "Перевод на счет")]


# Create your models here.
class Course(models.Model):
    """
    Модель курса уроков
    """

    name = models.CharField(max_length=150, verbose_name="Название")
    preview = models.ImageField(
        upload_to="mypedia/courses/previews/", blank=True, null=True
    )
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        null=True,
        blank=True,
        related_name="courses",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"

    def __str__(self):
        return self.name


class Lesson(models.Model):
    """
    Модель урока
    """

    name = models.CharField(max_length=150, verbose_name="Название")
    preview = models.ImageField(
        upload_to="mypedia/courses/previews/", blank=True, null=True
    )
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    video_link = models.TextField(verbose_name="Ссылка на видео", blank=True, null=True)
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс",
        null=True,
        blank=True,
        related_name="lessons",
    )
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        verbose_name="Владелец",
        null=True,
        blank=True,
        related_name="lessons",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"

    def __str__(self):
        return self.name


class Payment(models.Model):
    """
    Модель платежей сервиса
    """

    amount = models.PositiveIntegerField(verbose_name="Сумма оплаты")
    payment_method = models.CharField(
        max_length=25, choices=PAYMENT_METHODS, verbose_name="Способ оплаты"
    )
    payment_date = models.DateField(auto_now_add=True, verbose_name="Дата платежа")

    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        null=True,
        blank=True,
        related_name="payments",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Оплаченный курс",
        null=True,
        blank=True,
        related_name="payments",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        verbose_name="Оплаченный урок",
        null=True,
        blank=True,
        related_name="payments",
    )

    link = models.CharField(
        max_length=400, blank=True, null=True, verbose_name="Ссылка на оплату"
    )

    session_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ID сессии"
    )

    status = models.CharField(max_length=50, verbose_name="Статус", default="unpaid")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Платеж №{self.pk} от {self.payment_date} - {self.amount} руб."


class Subscription(models.Model):
    """
    Модель подписки на курс сервиса
    """

    is_active = models.BooleanField(verbose_name="Активна", default=True)
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="subscriptions",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Курс",
        related_name="subscriptions",
    )
    created_at = models.DateField(verbose_name="Дата активации", auto_now_add=True)

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"Подписка пользователя {self.owner.name} на курс {self.course.name} от {self.created_at}"
