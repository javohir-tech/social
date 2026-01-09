from django.urls import path
from .views import SingUpView, VerifyView, GetVerifyCode

urlpatterns = [
    path("singup/", SingUpView.as_view()),
    path("verify/", VerifyView.as_view()),
    path("qayta/", GetVerifyCode.as_view()),
]
