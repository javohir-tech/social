from django.urls import path
from .views import (
    SingUpView,
    VerifyView,
    GetVerifyCode,
    EditUserView,
    ChangeUserPhotoView,
)

urlpatterns = [
    path("singup/", SingUpView.as_view()),
    path("verify/", VerifyView.as_view()),
    path("qayta/", GetVerifyCode.as_view()),
    path("change/", EditUserView.as_view()),
    path("photo/", ChangeUserPhotoView.as_view()),
]
