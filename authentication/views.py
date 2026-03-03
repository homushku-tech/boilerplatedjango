from datetime import timedelta

"""Импорты DRF"""
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied

"""Импорты drf_spectacular"""
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

"""Импорты Django"""
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

"""Локальные импорты"""
from authentication.models import CustomUser, EmailVerificationModel, PasswordResetCodeModel
from authentication.serializer import (
    RegisterSerializer,
    LoginSerializer,
    VerificationSerializer,
    ResendCodeSerializer,
    PasswordResetRequestSerialiazer,
    PasswordResetSerialiazer,
)
from authentication.utils import generate_strong_6_digit_number, send_verification_email


@extend_schema(tags=["Профиль"])
class RegisterUser(CreateAPIView):
    """
    Представление для регистрации пользователей в системе

    * email: user@example.com
    * username: 3-8 символов, разрешены только буквы, цифры, подчеркивания и точки
    * password: минимум 8 символов

    При успешной регистрации код подтверждения отправляется на email пользователя
    """

    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        verification_code = generate_strong_6_digit_number()
        code_data = EmailVerificationModel.objects.create(
            user=serializer.instance, code=verification_code
        )

        # Пользовательские данные ответа
        custom_data = {
            "registration_success": True,
            "message": "Аккаунт успешно создан.",
            "email": serializer.data["email"],
            "username": serializer.data["username"],
        }

        headers = self.get_success_headers(serializer.data)

        return Response(custom_data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(tags=["Профиль"])
class LoginUser(APIView):
    """
    Представление для входа пользователей в систему

    * email
    * password
    """

    serializer_class = LoginSerializer

    def post(self, request):

        serializer_class = LoginSerializer(
            data=request.data, context={"request": request}
        )

        serializer_class.is_valid(raise_exception=True)

        user = serializer_class.validated_data["user"]

        full_user_data = CustomUser.objects.filter(email=user.email).values()

        user_data = full_user_data.first()

        user_data_returned = {
            "id": user_data["id"],
            "email": user_data["email"],
            "username": user_data["username"],
            "is_staff": user_data["is_staff"],
            "is_superuser": user_data["is_superuser"],
            "is_verified": user_data["is_verified"],
        }

        # Выпуск JWT токенов
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_data": user_data_returned,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Верификация"],
    responses={
        200: OpenApiResponse(description="Email подтвержден"),
        404: OpenApiResponse(description="Что-то пошло не так."),
        500: OpenApiResponse(description="Произошла непредвиденная ошибка при повторной отправке кода подтверждения."),
    },
)
class Verification(APIView):
    """
    Представление для верификации пользователей путем проверки кода подтверждения

    * email: email пользователя, на который был отправлен код
    * code: код, полученный на email
    """

    serializer_class = VerificationSerializer

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            email = data.get("email")
            entered_code = data.get("code")

            user = CustomUser.objects.get(email=email)

            code_data = EmailVerificationModel.objects.get(user=user.id)

            if user.is_verified:
                return Response({"error": "Пользователь уже подтвержден"}, status=400)

            if code_data.code != entered_code:
                return Response({"error": "Неверный код"}, status=400)

            if code_data.is_expired:
                return Response({"error": "Срок действия кода истек"}, status=400)
            user.code_expires_at = None

            user.is_verified = True
            user.save()

            code_data.code = None
            code_data.save()

            return Response(
                {"detail": "Email подтвержден."},
                status=status.HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            raise NotFound(detail=f"Что-то пошло не так.", status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response(
                {
                    "detail": "Произошла непредвиденная ошибка при повторной отправке кода подтверждения.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["Верификация"],
    responses={
        200: OpenApiResponse(description="Код успешно отправлен"),
        400: OpenApiResponse(description="Неверный email"),
        404: OpenApiResponse(description="Пользователь не найден"),
    },
)
class ResendCodeEmailVerificationCode(APIView):
    """
    Повторная отправка кода подтверждения на email пользователя для верификации email

    - email
    """

    serializer_class = ResendCodeSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")

        try:
            # Получение пользователя по email
            user = CustomUser.objects.get(email=email)

            # Если уже подтвержден, не отправлять повторно
            if user.is_verified:
                return Response(
                    {"detail": "Пользователь уже подтвержден."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Генерация и сохранение нового кода, если не существует - обновить
            verification_code = generate_strong_6_digit_number()

            verification_instance, created = (
                EmailVerificationModel.objects.update_or_create(
                    user=user,
                    defaults={
                        "code": verification_code,
                        "expires_at": timezone.now() + timedelta(minutes=15),
                    },
                )
            )

            # Повторная отправка email
            if send_verification_email(code=str(verification_code), email=user.email):
                # В целях безопасности не сообщаем пользователю, существует ли email
                return Response(
                    {
                        "detail": "Если этот email существует, код для подтверждения был отправлен.",
                        "email": user.email,
                    },
                    status=status.HTTP_200_OK,
                )

        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"Если этот email существует, код для подтверждения был отправлен. '{email}'."
            )

        except Exception as e:
            return Response(
                {
                    "detail": "Произошла непредвиденная ошибка при повторной отправке кода подтверждения.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=["Пароль"])
class PasswordCodeResetRequest(APIView):
    """
    Представление для запроса кода подтверждения для сброса пароля пользователя

    - email: для получения кода
    """

    serializer_class = PasswordResetRequestSerialiazer

    def post(self, request):
        email = request.data["email"]

        try:
            # Проверка существования пользователя
            user_data = CustomUser.objects.get(email=email)

            # Генерация нового 6-значного кода
            verification_code = generate_strong_6_digit_number()

            # Создание объекта PasswordResetCode, если не существует
            password_reset_instance, created = (
                PasswordResetCodeModel.objects.update_or_create(
                    user=user_data,
                    defaults={
                        "code": verification_code,
                        "expires_at": timezone.now() + timedelta(minutes=15),
                    },
                )
            )

            if send_verification_email(
                code=str(verification_code),
                email=email,
            ):
                return Response(
                    {
                        "message": "Если этот email существует, код для сброса пароля был отправлен."
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"error": "Что-то пошло не так"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except ObjectDoesNotExist:
            return Response(
                {
                    "error": "Если этот email существует, код для сброса пароля был отправлен."
                },
                status=400,
            )
        except Exception as e:
            return Response(
                {
                    "detail": "Произошла непредвиденная ошибка при запросе кода для сброса пароля.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=["Пароль"])
class PasswordReset(APIView):
    """
    Представление для сброса пароля пользователя в системе

    - email: email пользователя
    - code: код подтверждения, отправленный на email пользователя
    - new_password: новый пароль, который пользователь хочет установить
    """

    serializer_class = PasswordResetSerialiazer

    def patch(self, request):
        email = request.data["email"]
        code = request.data["code"]
        new_password = request.data["new_password"]

        try:
            # Проверка существования пользователя
            user = CustomUser.objects.get(email=email)

            reset_code = PasswordResetCodeModel.objects.get(user=user.id)

            # Проверка соответствия кода, предоставленного пользователем, коду в БД сброса пароля
            if reset_code.code == code:
                # Хеширование и обновление нового пароля в БД пользователя
                # Установка кода в БД сброса пароля в NULL
                # Сохранение
                user.set_password(raw_password=new_password)
                user.is_verified = True
                user.save()

                reset_code.code = None
                reset_code.save()

                return Response(
                    {"message": "Сброс пароля выполнен успешно."}, status=status.HTTP_200_OK
                )
            else:
                return Response({"error": "Неверный код."}, status=400)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Сначала запросите код для сброса пароля"},
                status=400,
            )
        except Exception as e:
            return Response(
                {
                    "detail": "Произошла непредвиденная ошибка при сбросе пароля.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )