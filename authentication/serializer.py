import re

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from authentication.models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "username", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {
                "error_messages": {
                    "max_length": "Username must be between 3 and 8 characters long."
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
                "Only letters, numbers, underscores, and dots are allowed."
            )

        if len(username) < 3 or len(username) > 8:
            raise serializers.ValidationError(
                "Username must be between 3 to 8 characters long."
            )

        if CustomUser.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("User with this username already exists.")

        return username

    def validate_email(self, value):
        email = value.lower()

        if CustomUser.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("User with this email already exists.")

        return email

    def create(self, validated_data):
        user = CustomUser(
            email=validated_data["email"], username=validated_data["username"]
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        if not identifier or not password:
            raise serializers.ValidationError(
                "Both identifier and password are required."
            )

        if "@" in identifier:
            try:
                user_obj = CustomUser.objects.get(email__iexact=identifier)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            try:
                user_obj = CustomUser.objects.get(username__iexact=identifier)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Invalid username or password.")

        user = authenticate(
            request=self.context.get("request"),
            email=user_obj.email,
            password=attrs["password"],
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        attrs["user"] = user
        return attrs
