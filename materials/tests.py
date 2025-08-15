from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from users.models import User

from .models import Course, Lesson, Subscription


# Create your tests here.
class LessonTestCase(APITestCase):
    """
    Тестирование функционала контроллеров Lesson
    """

    def setUp(self):
        """
        Подготовка исходных данных
        """

        self.user = User.objects.create(email="test@email.com")
        self.moderator = User.objects.create(email="moderator@email.com")
        group = Group.objects.create(name="Moderators")
        self.moderator.groups.add(group)

        self.lesson = Lesson.objects.create(
            name="Тестовый урок 1", description="Первый тестовый урок", owner=self.user
        )
        self.lesson_2 = Lesson.objects.create(
            name="Тестовый урок 2", description="Второй тестовый урок"
        )
        self.client.force_authenticate(self.user)

    def test_lesson_retrieve(self):
        """
        Тест просмотра объекта Lesson
        """

        # Обычный пользователь - собственный урок
        url = reverse("materials:lesson", args=[self.lesson.pk])
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.lesson.name)

        # Обычный пользователь - чужой урок
        url = reverse("materials:lesson", args=[self.lesson_2.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Модератор
        self.client.force_authenticate(self.moderator)
        url = reverse("materials:lesson", args=[self.lesson.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.lesson.name)

    def test_lesson_create(self):
        """
        Тест создания объекта Lesson и автоматического заполнения поля owner
        """

        # Обычный пользователь
        url = reverse("materials:lessons")
        data = {"name": "Тестовый урок 3", "description": "Третий тестовый урок"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["owner"], self.user.pk)
        self.assertEqual(Lesson.objects.all().count(), 3)

        # Модератор
        self.client.force_authenticate(self.moderator)
        url = reverse("materials:lessons")
        data = {"name": "Тестовый урок 3", "description": "Третий тестовый урок"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update(self):
        """
        Тест обновления объекта Lesson и корректного заполнения поля video_link
        """

        # Обычный пользователь - свой урок
        url = reverse("materials:lesson", args=[self.lesson.pk])
        data = {"video_link": "https://www.youtube.com/..."}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("video_link"), "https://www.youtube.com/...")

        # Обычный пользователь - чужой урок
        url = reverse("materials:lesson", args=[self.lesson_2.pk])
        data = {"video_link": "https://www.youtube.com/..."}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Модератор
        self.client.force_authenticate(self.moderator)
        url = reverse("materials:lesson", args=[self.lesson.pk])
        data = {"video_link": "https://www.youtube.com"}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("video_link"), "https://www.youtube.com")

    def test_invalid_video_link(self):
        """
        Тест некорректного заполнения поля video_link
        """

        url = reverse("materials:lesson", args=[self.lesson.pk])
        data = {"video_link": "https://www.google.com/..."}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaisesRegex(
            ValidationError, "Ссылка может быть только видео сервис youtube.com"
        )

    # def test_lesson_delete(self):
    #     """
    #     Тест удаления объекта Lesson
    #     """
    #
    #     # Обычный пользователь - свой урок
    #     url = reverse("materials:lesson", args=[self.lesson.pk])
    #     response = self.client.delete(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertEqual(Lesson.objects.all().count(), 1)
    #
    #     # Обычный пользователь - чужой урок
    #     url = reverse("materials:lesson", args=[self.lesson_2.pk])
    #     response = self.client.delete(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertEqual(Lesson.objects.all().count(), 1)
    #
    #     # Модератор
    #     self.client.force_authenticate(self.moderator)
    #     url = reverse("materials:lesson", args=[self.lesson_2.pk])
    #     response = self.client.delete(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #
    #
    #     # Модератор
    #     self.client.force_authenticate(self.moderator)
    #     url = reverse("materials:lessons")
    #     response = self.client.get(url)
    #     data = response.json()
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #
    #     result = {
    #         "count": 2,
    #         "next": None,
    #         "previous": None,
    #         "results": [
    #             {
    #                 "id": self.lesson.pk,
    #                 "name": self.lesson.name,
    #                 "preview": self.lesson.preview,
    #                 "description": self.lesson.description,
    #                 "video_link": self.lesson.video_link,
    #                 "updated_at": self.lesson.updated_at.strftime(
    #                     "%Y-%m-%dT%H:%M:%S.%fZ"
    #                 ),
    #                 "course": None,
    #                 "owner": self.lesson.owner.pk,
    #             },
    #             {
    #                 "id": self.lesson_2.pk,
    #                 "name": self.lesson_2.name,
    #                 "preview": self.lesson_2.preview,
    #                 "description": self.lesson_2.description,
    #                 "video_link": self.lesson_2.video_link,
    #                 "updated_at": self.lesson_2.updated_at.strftime(
    #                     "%Y-%m-%dT%H:%M:%S.%fZ"
    #                 ),
    #                 "course": None,
    #                 "owner": None,
    #             },
    #         ],
    #     }
    #
    #     self.assertEqual(data, result)


class CourseSubscriptionTestCase(APITestCase):
    """
    Тестирование функционала контроллеров Course и Subscription
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
            name="Тестовый курс 1", description="Первый тестовый курс", owner=self.user
        )
        self.course_2 = Course.objects.create(
            name="Тестовый курс 2", description="Второй тестовый курс"
        )

        self.lesson = Lesson.objects.create(
            name="Тестовый урок 1",
            description="Первый тестовый урок",
            course=self.course,
            owner=self.user,
        )

        self.subscription = Subscription.objects.create(
            course=self.course, owner=self.user
        )
        self.subscription_2 = Subscription.objects.create(
            course=self.course_2, owner=self.moderator
        )

        self.client.force_authenticate(self.user)

    def test_subscription_retrieve(self):
        """
        Тест просмотра объекта Subscription
        """

        # Обычный пользователь - своя подписка
        url = reverse("materials:subscription", args=[self.subscription.pk])
        response = self.client.get(url)
        data = response.json()
        result = {
            "id": self.subscription.pk,
            "is_active": self.subscription.is_active,
            "created_at": self.subscription.created_at.isoformat(),
            "owner": self.user.pk,
            "course": self.course.pk,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

        # Обычный пользователь - чужая подписка
        url = reverse("materials:subscription", args=[self.subscription_2.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Модератор
        self.client.force_authenticate(self.moderator)
        url = reverse("materials:subscription", args=[self.subscription.pk])
        response = self.client.get(url)
        data = response.json()
        result = {
            "id": self.subscription.pk,
            "is_active": self.subscription.is_active,
            "created_at": self.subscription.created_at.isoformat(),
            "owner": self.user.pk,
            "course": self.course.pk,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

    def test_subscription_create(self):
        """
        Тест создания объекта Subscription
        """

        # Обычный пользователь
        url = reverse("materials:subscriptions")
        data = {"course": self.course_2.pk, "owner": self.user.pk}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Модератор
        self.client.force_authenticate(user=self.moderator)
        url = reverse("materials:subscriptions")
        data = {"course": self.course_2.pk, "owner": self.user.pk}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["owner"], self.user.pk)
        self.assertEqual(Subscription.objects.all().count(), 3)

    def test_subscription_update(self):
        """
        Тест изменения объекта Subscription
        """

        # Обычный пользователь
        url = reverse("materials:subscription", args=[self.subscription.pk])
        data = {"is_active": False}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Модератор
        self.client.force_authenticate(user=self.moderator)
        url = reverse("materials:subscription", args=[self.subscription.pk])
        data = {"is_active": False}
        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["is_active"], False)

    def test_subscription_delete(self):
        """
        Тест удаления объекта Subscription
        """

        # Обычный пользователь
        url = reverse("materials:subscription", args=[self.subscription.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Модератор
        self.client.force_authenticate(user=self.moderator)
        url = reverse("materials:subscription", args=[self.subscription.pk])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Subscription.objects.all().count(), 1)

    def test_subscription_list(self):
        """
        Тест просмотра списка объектов Subscription
        """

        # Обычный пользователь
        url = reverse("materials:subscriptions")
        response = self.client.get(url)
        data = response.json()
        result = [
            {
                "id": self.subscription.pk,
                "is_active": self.subscription.is_active,
                "created_at": self.subscription.created_at.isoformat(),
                "owner": self.user.pk,
                "course": self.course.pk,
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

        # Модератор
        self.client.force_authenticate(self.moderator)
        url = reverse("materials:subscriptions")
        response = self.client.get(url)
        data = response.json()
        result = [
            {
                "id": self.subscription.pk,
                "is_active": self.subscription.is_active,
                "created_at": self.subscription.created_at.isoformat(),
                "owner": self.user.pk,
                "course": self.course.pk,
            },
            {
                "id": self.subscription_2.pk,
                "is_active": self.subscription_2.is_active,
                "created_at": self.subscription_2.created_at.isoformat(),
                "owner": self.moderator.pk,
                "course": self.course_2.pk,
            },
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, result)

    def test_course_retrieve(self):
        """
        Тест просмотра объекта Course
        """

        # Обычный пользователь - собственный курс
        url = reverse("materials:courses-detail", args=[self.course.pk])
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.course.name)

        # Обычный пользователь - чужой курс
        url = reverse("materials:courses-detail", args=[self.course_2.pk])
        response = self.client.get(url)

        self.assertEqual(
            response.status_code, status.HTTP_404_NOT_FOUND
        )  # queryset даже не включает чужие объекты

        # Модератор
        self.client.force_authenticate(self.moderator)
        url = reverse("materials:courses-detail", args=[self.course.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data.get("name"), self.course.name)

    def test_course_create(self):
        """
        Тест создания объекта Course и автоматического заполнения поля owner
        """

        # Обычный пользователь
        url = reverse("materials:courses-list")
        data = {"name": "Тестовый курс 3", "description": "Третий тестовый курс"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["owner"], self.user.pk)
        self.assertEqual(Course.objects.all().count(), 3)

        # Модератор
        self.client.force_authenticate(self.moderator)
        url = reverse("materials:courses-list")
        data = {"name": "Тестовый курс 3", "description": "Третий тестовый курс"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # def test_course_delete(self):
    #     """
    #     Тест удаления объекта Course
    #     """
    #
    #     # Обычный пользователь - свой курс
    #     url = reverse("materials:courses-detail", args=[self.course.pk])
    #     response = self.client.delete(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertEqual(Course.objects.all().count(), 1)  # После удаления остался только course_2
    #
    #     # Обычный пользователь - чужой курс
    #     url = reverse("materials:courses-detail", args=[self.course_2.pk])
    #     response = self.client.delete(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    #
    #     # Модератор пытается удалить course_2
    #     self.client.force_authenticate(self.moderator)
    #     url = reverse("materials:courses-detail", args=[self.course_2.pk])
    #     response = self.client.delete(url)
    #
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #
    #     # Проверка списка курсов после удаления
    #     self.client.force_authenticate(self.moderator)
    #     url = reverse("materials:courses-list")
    #     response = self.client.get(url)
    #     data = response.json()
    #
    #     # Ожидаемый результат: только course_2, так как course был удален
    #     result = {
    #         "count": 1,
    #         "next": None,
    #         "previous": None,
    #         "results": [
    #             {
    #                 "id": self.course_2.pk,
    #                 "lessons_count": 0,
    #                 "course_lessons": [],
    #                 "is_subscribed": "Вы подписаны",  # или другое ожидаемое значение
    #                 "name": self.course_2.name,
    #                 "preview": self.course_2.preview,
    #                 "description": self.course_2.description,
    #                 "updated_at": self.course_2.updated_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
    #                 "owner": self.course_2.owner.pk if self.course_2.owner else None,  # проверьте владельца
    #             }
    #         ],
    #     }
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(data, result)
