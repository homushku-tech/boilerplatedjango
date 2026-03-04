from authentication.views import LoginUser, RegisterUser
from django.urls import path


urlpatterns = [
    path("register/", RegisterUser.as_view(), name="register"),
    path("login/", LoginUser.as_view(), name="login"),
]
