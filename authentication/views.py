from authentication.models import CustomUser
from authentication.serializer import LoginSerializer, RegisterSerializer
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


@extend_schema(tags=["Профиль"])
class RegisterUser(CreateAPIView):
    """
    Представление для регистрации пользователей в системе
    * email: user@example.com
    * username: 3-8 символов, разрешены только буквы, цифры, подчеркивания и точки
    * password: минимум 8 символов
    """

    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        custom_data = {
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
    email/username
    password
    """

    serializer_class = LoginSerializer

    def post(self, request):

        serializer_class = LoginSerializer(data=request.data, context={"request": request})

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

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_data": user_data_returned,
            },
            status=status.HTTP_200_OK,
        )
