from django.urls import path
from .views import PostListView, CreatePostView

urlpatterns = [
    path("posts/", PostListView.as_view()),
    path("create/", CreatePostView.as_view()),
]
