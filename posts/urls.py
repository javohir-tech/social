from django.urls import path
from .views import (
    PostListView,
    CreatePostView,
    RetriveView,
    CommentListCreateView,
    PostLikesView,
    PostCommentView,
    CommentRetriveView,
    CommentLikeList,
    PostLikeView,
    CommentLikeView,
)

urlpatterns = [
    path("posts/", PostListView.as_view()),
    path("<uuid:pk>/likes/", PostLikesView.as_view()),
    path("create/", CreatePostView.as_view()),
    path("detail/<uuid:pk>/", RetriveView.as_view()),
    path("<uuid:pk>/comments/", PostCommentView.as_view()),
    path("comments/", CommentListCreateView.as_view()),
    path("comments/create/", CommentListCreateView.as_view()),
    path("comments/<uuid:pk>/", CommentRetriveView.as_view()),
    path("comments/<uuid:pk>/likes/", CommentLikeList.as_view()),
    path("<uuid:pk>/post-like-dislike/", PostLikeView.as_view()),
    path("<uuid:pk>/comment-like-dislike/", CommentLikeView.as_view()),
]
