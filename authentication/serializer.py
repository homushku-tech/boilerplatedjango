import re

from authentication.models import CustomUser
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "username", "password"]
        extra_kwargs = {
            "password": {"write_only": True},  # Только для записи
            "username": {
                "error_messages": {
                    "max_length": "Имя пользователя должно содержать от 3 до 8 символов."
                }
            },
        }

    def validate_password(self, value):
        try:
            validate_password(value, self.instance)
        except Exception as e:
            raise serializers.ValidationError({"password": list(e)})

        return value

    def validate_username(self, value):
        username = value.lower()

        if not re.match(r"^[a-zA-Z0-9_.]+$", username):
            raise serializers.ValidationError(
                "Разрешены только буквы, цифры, символы подчеркивания и точки."
            )

        if len(username) < 3 or len(username) > 8:
            raise serializers.ValidationError(
                "Имя пользователя должно содержать от 3 до 8 символов."
            )

        if CustomUser.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует.")

        return username

    def validate_email(self, value):
        email = value.lower()

        if CustomUser.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")

        return email

    def create(self, validated_data):
        user = CustomUser(email=validated_data["email"], username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()  # Идентификатор (email или имя пользователя)
    password = serializers.CharField(write_only=True)  # Только для записи

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        if not identifier or not password:
            raise serializers.ValidationError("Необходимо указать идентификатор и пароль.")

        if "@" in identifier:
            try:
                user_obj = CustomUser.objects.get(email__iexact=identifier)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Неверный email или пароль.")
        else:
            try:
                user_obj = CustomUser.objects.get(username__iexact=identifier)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Неверное имя пользователя или пароль.")

        user = authenticate(
            request=self.context.get("request"),
            email=user_obj.email,
            password=attrs["password"],
        )

        if not user:
            raise serializers.ValidationError("Неверные учетные данные")

        attrs["user"] = user
        return attrs
