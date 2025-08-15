from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from materials.models import Course, Lesson, Payment

from .models import User


# Create your tests here.
class UserTestCase(APITestCase):
    """
    Тестирование функционала контроллеров User
    """

    def setUp(self):
        """
        Подготовка исходных данных
        """

        self.user = User.objects.create(email="test@email.com")
        self.user.set_password("12345")
        self.user.save()
        self.admin = User.objects.create(
            email="admin@email.com", is_staff=True, is_superuser=True
        )
        self.moderator = User.objects.create(email="moderator@email.com")
        group = Group.objects.create(name="Moderators")
        self.moderator.groups.add(group)

        self.client.force_authenticate(self.user)

    def test_user_retrieve(self):
        """
        Тест просмотра объекта User
        """

        # Обычный пользователь - собственный профиль
        url = reverse("users:user", args=[self.user.pk])
        response = self.client.get(url)
        data = response.json()
        data_keys = [key for key in data.keys()]
        result_keys = [
            "id",
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "country",
            "avatar",
            "payments_history",
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data_keys, result_keys)

        # Обычный пользователь - чужой профиль
        url = reverse("users:user", args=[self.moderator.pk])
        response = self.client.get(url)
        data = response.json()
        data_keys = [key for key in data.keys()]
        result_keys = ["id", "email", "username", "first_name", "country", "avatar"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data_keys, result_keys)

        # Админ
        self.client.force_authenticate(self.admin)
        url = reverse("users:user", args=[self.user.pk])
        response = self.client.get(url)
        data = response.json()
        data_keys = [key for key in data.keys()]
        result_keys = [
            "id",
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "country",
            "avatar",
            "payments_history",
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data_keys, result_keys)

    def test_user_create(self):
        """
        Тест создания объекта User и автоматической активации учетной записи
        """

        url = reverse("users:users")
        data = {"email": "test2@email.com", "password": "12345"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["is_active"], True)
        self.assertEqual(User.objects.all().count(), 4)

    def test_user_update(self):
        """
        Тест обновления объекта User
        """

        # Обычный пользователь - свой профиль
        url = reverse("users:user", args=[self.user.pk])
        data = {"username": "test"}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "test")

        # Обычный пользователь - чужой профиль
        url = reverse("users:user", args=[self.moderator.pk])
        data = {"username": "test"}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Модератор - общедоступные данные
        self.client.force_authenticate(self.moderator)
        url = reverse("users:user", args=[self.user.pk])
        data = {"username": "test"}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["username"], "test")

        # Модератор - конфиденциальные данные
        self.client.force_authenticate(self.moderator)
        url = reverse("users:user", args=[self.user.pk])
        data = {"phone_number": "8-800-555-35-35"}
        response = self.client.patch(url, data)

        with self.assertRaises(KeyError):  # данные не обработаются сериализатором
            response.json()["phone_number"]

        # Админ - конфиденциальные данные
        self.client.force_authenticate(self.admin)
        url = reverse("users:user", args=[self.user.pk])
        data = {"phone_number": "8-800-555-35-35"}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["phone_number"], "8-800-555-35-35")

    def test_user_delete(self):
        """
        Тест удаления объекта User
        """

        # Обычный пользователь - свой профиль
        url = reverse("users:user", args=[self.user.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.all().count(), 2)

        # Обычный пользователь - чужой профиль
        url = reverse("users:user", args=[self.moderator.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Админ
        self.client.force_authenticate(self.admin)
        url = reverse("users:user", args=[self.moderator.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.all().count(), 1)

    def test_user_list(self):
        """
        Тест вывода списка объектов User
        """

        url = reverse("users:users")
        response = self.client.get(url)
        data = response.json()
        result = [
            {
                "id": self.user.pk,
                "email": self.user.email,
                "username": self.user.username,
                "first_name": self.user.first_name,
                "country": self.user.country,
                "avatar": None,
            },
            {
                "id": self.admin.pk,
                "email": self.admin.email,
                "username": self.admin.username,
                "first_name": self.admin.first_name,
                "country": self.admin.country,
                "avatar": None,
            },
            {
                "id": self.moderator.pk,
                "email": self.moderator.email,
                "username": self.moderator.username,
                "first_name": self.moderator.first_name,
                "country": self.moderator.country,
                "avatar": None,
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

    def test_login_refresh(self):
        """
        Тест авторизации и получения access и refresh токенов
        """
        self.client.logout()

        # Проверка авторизации
        url = reverse("users:login")
        data = {"email": "test@email.com", "password": "12345"}
        response = self.client.post(url, data)
        result = response.json()
        result_keys = [key for key in result.keys()]

        self.assertEqual(result_keys, ["refresh", "access"])

        # Проверка обновления access токена по refresh токену
        url = reverse("users:token-refresh")
        data = {"refresh": result["refresh"]}
        response = self.client.post(url, data)
        result = response.json()

        self.assertTrue(result.get("access"))


class PaymentTestCase(APITestCase):
    """
    Тестирование функционала контроллеров Payment
    """

    def setUp(self):
        """
        Подготовка исходных данных
        """

        self.user = User.objects.create(email="test@email.com")
        self.moderator = User.objects.create(email="moderator@email.com")
        group = Group.objects.create(name="Moderators")
        self.moderator.groups.add(group)

        self.course = Course.objects.create(
            name="Тестовый курс 1", description="Первый тестовый курс"
        )
        self.lesson = Lesson.objects.create(
            name="Тестовый урок 1", description="Первый тестовый урок"
        )
        self.payment = Payment.objects.create(
            amount=2500, payment_method="cash", course=self.course, owner=self.user
        )
        self.payment_2 = Payment.objects.create(
            amount=5000, payment_method="transfer_to_account", lesson=self.lesson
        )

        self.client.force_authenticate(self.user)

    def test_payment_retrieve(self):
        """
        Тест просмотра объекта Payment
        """

        # Обычный пользователь - собственный платеж
        url = reverse("users:payment", args=[self.payment.pk])
        response = self.client.get(url)
        data = response.json()
        result = {
            "id": self.payment.pk,
            "amount": self.payment.amount,
            "payment_method": self.payment.payment_method,
            "payment_date": self.payment.payment_date.isoformat(),
            "link": self.payment.link,
            "session_id": self.payment.session_id,
            "status": self.payment.status,
            "owner": self.payment.owner.pk,
            "course": self.payment.course.pk,
            "lesson": None,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

        # Обычный пользователь - чужой платеж
        url = reverse("users:payment", args=[self.payment_2.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Модератор
        self.client.force_authenticate(self.moderator)
        url = reverse("users:payment", args=[self.payment.pk])
        response = self.client.get(url)
        data = response.json()
        result = {
            "id": self.payment.pk,
            "amount": self.payment.amount,
            "payment_method": self.payment.payment_method,
            "payment_date": self.payment.payment_date.isoformat(),
            "link": self.payment.link,
            "session_id": self.payment.session_id,
            "status": self.payment.status,
            "owner": self.payment.owner.pk,
            "course": self.payment.course.pk,
            "lesson": None,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

    def test_payment_create(self):
        """
        Тест создания объекта Payment, автоматического заполнения поля owner и создания платежа в stripe
        """

        url = reverse("users:payments")
        data = {"amount": 10000, "payment_method": "cash", "lesson": self.lesson.pk}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["owner"], self.user.pk)
        self.assertTrue(
            all([response.json().get("link"), response.json().get("session_id")])
        )
        self.assertEqual(Payment.objects.all().count(), 3)

    def test_payment_update(self):
        """
        Тест обновления объекта Payment
        """

        # Обычный пользователь
        url = reverse("users:payment", args=[self.payment.pk])
        data = {"amount": 1000000}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Модератор
        self.client.force_authenticate(self.moderator)
        url = reverse("users:payment", args=[self.payment.pk])
        data = {"amount": 0}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("amount"), 0)

    def test_payment_delete(self):
        """
        Тест удаления объекта Payment
        """

        # Обычный пользователь
        url = reverse("users:payment", args=[self.payment.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Модератор
        self.client.force_authenticate(self.moderator)
        url = reverse("users:payment", args=[self.payment.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Payment.objects.all().count(), 1)

    def test_payment_list(self):
        """
        Тест вывода списка объектов Payment
        """

        # Обычный пользователь
        url = reverse("users:payments")
        response = self.client.get(url)
        data = response.json()
        result = [
            {
                "id": self.payment.pk,
                "amount": self.payment.amount,
                "payment_method": self.payment.payment_method,
                "payment_date": self.payment.payment_date.isoformat(),
                "link": self.payment.link,
                "session_id": self.payment.session_id,
                "status": self.payment.status,
                "owner": self.payment.owner.pk,
                "course": self.payment.course.pk,
                "lesson": None,
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

        # Модератор
        self.client.force_authenticate(self.moderator)
        url = reverse("users:payments")
        response = self.client.get(url)
        data = response.json()

        result = [
            {
                "id": self.payment.pk,
                "amount": self.payment.amount,
                "payment_method": self.payment.payment_method,
                "payment_date": self.payment.payment_date.isoformat(),
                "link": self.payment.link,
                "session_id": self.payment.session_id,
                "status": self.payment.status,
                "owner": self.payment.owner.pk,
                "course": self.payment.course.pk,
                "lesson": None,
            },
            {
                "id": self.payment_2.pk,
                "amount": self.payment_2.amount,
                "payment_method": self.payment_2.payment_method,
                "payment_date": self.payment_2.payment_date.isoformat(),
                "link": self.payment_2.link,
                "session_id": self.payment_2.session_id,
                "status": self.payment_2.status,
                "owner": None,
                "course": None,
                "lesson": self.payment_2.lesson.pk,
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)
