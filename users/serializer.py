from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для реализации CRUD операций для пользователя"""

    class Meta:
        model = User
        fields = ("id", "email", "name", "surname", "patronymic", "position", "password", "avatar", "phone", "city")
        validators = [
            serializers.UniqueTogetherValidator(
                fields=["email", "name", "surname", "patronymic",],
                queryset=User.objects.all()),
        ]
