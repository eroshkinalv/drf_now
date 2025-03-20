import stripe
from django.contrib.auth.models import Group

from conf.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


def get_queryset_for_owner(user, queryset):
    try:
        if user.is_superuser or user.groups.get(name="Moderators"):
            return queryset.order_by("id")
    except Group.DoesNotExist:
        return queryset.filter(owner=user).order_by("id")


def create_stripe_product(instance):
    """
    Создания продукта в stripe
    """
    instance_name = (
        f"Оплата курса {instance.course.name}"
        if instance.course
        else f"Оплата урока {instance.lesson.name}"
    )
    return stripe.Product.create(name=instance_name)


def create_stripe_price(instance):
    """
    Создание цены в stripe
    """
    return stripe.Price.create(
        currency="rub",
        unit_amount=instance.amount * 100,
        product=create_stripe_product(instance).get("id"),
    )


def create_stripe_session(price):
    """
    Создание сессии на оплату в stripe
    """
    session = stripe.checkout.Session.create(
        success_url="https://127.0.0.1:8000/payments/",
        line_items=[{"price": price.get("id"), "quantity": 1}],
        mode="payment",
    )
    return session.get("id"), session.get("url")


def check_session_status(session_id):
    """
    Уточнение статуса сессии
    """
    return stripe.checkout.Session.retrieve(session_id).get("payment_status")
