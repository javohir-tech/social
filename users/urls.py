from django.urls import path
from .views import SingUpView, VerifyView

urlpatterns = [
    path("singup/", SingUpView.as_view()),
    path("verify/", VerifyView.as_view()),
]
