from rest_framework import serializers

from materials.serializers import PaymentSerializer

from .models import User


class NewUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User для авторизации пользователя
    """

    class Meta:
        model = User
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User
    """

    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "country", "avatar"]


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детальной информации об объекте модели User
    """

    payments_history = PaymentSerializer(source="payments", many=True)

    class Meta:
        model = User
        fields = [
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
