from django.urls import path
from .views import PostListView, CreatePostView, RetriveView, CommentListCreateView

urlpatterns = [
    path("posts/", PostListView.as_view()),
    path("create/", CreatePostView.as_view()),
    path("detail/<uuid:pk>/", RetriveView.as_view()),
    path("<uuid:pk>/comments/", CommentListCreateView.as_view()),
    path("comments/create/", CommentListCreateView.as_view()),
]
