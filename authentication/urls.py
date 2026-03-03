from django.urls import path, include
from authentication.views import (
    RegisterUser,
    LoginUser,
    Verification,
    ResendCodeEmailVerificationCode,
    PasswordCodeResetRequest,
    PasswordReset,
)

urlpatterns = [
    # профиль
    path("register/", RegisterUser.as_view(), name="register"),
    path("login/", LoginUser.as_view(), name="login"),
    # верификация
    path("verify-email/", Verification.as_view(), name="verify-email"),
    path("resend-verification/", ResendCodeEmailVerificationCode.as_view(), name="resend-code"),
    # пароли
    path("reset-password-request/", PasswordCodeResetRequest.as_view(), name="reset-request"),
    path("reset-password/", PasswordReset.as_view(), name="reset"),
]
