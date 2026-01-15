from django.urls import path
from .views import PostListView, CreatePostView, RetriveView

urlpatterns = [
    path("posts/", PostListView.as_view()),
    path("create/", CreatePostView.as_view()),
    path("detail/<uuid:pk>/", RetriveView.as_view()),
]
