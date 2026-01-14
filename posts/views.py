from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Post, PostComment, PostLike, CommentLike
from .serializers import (
    PostSerializer,
    PostCommentSerializer,
    PostLikeSerializer,
    CommentLikeSerializer,
)
from shared.custom_pagiation import CustomPagination

class PostListView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()


# Create your views here.
