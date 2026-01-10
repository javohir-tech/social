from django.urls import path
from .views import (
    SingUpView,
    VerifyView,
    GetVerifyCode,
    EditUserView,
    ChangeUserPhotoView,
    LoginView,
    RefreshTokenView, 
    ForgetPasswordView
)

urlpatterns = [
    path("login/", LoginView.as_view()),
    path("login/forget/", ForgetPasswordView.as_view()),
    path("singup/", SingUpView.as_view()),
    path("verify/", VerifyView.as_view()),
    path("qayta/", GetVerifyCode.as_view()),
    path("change/", EditUserView.as_view()),
    path("photo/", ChangeUserPhotoView.as_view()),
    path("refresh/" , RefreshTokenView.as_view())
]
