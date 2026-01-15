from django.shortcuts import render
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView
)
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
)
from .models import Post, PostComment, PostLike, CommentLike
from .serializers import (
    PostSerializer,
    PostCommentSerializer,
    PostLikeSerializer,
    CommentLikeSerializer,
)
from shared.custom_pagiation import CustomPagination
from rest_framework.response import Response
from rest_framework import status


class PostListView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()


class CreatePostView(CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)
        return Response(
            {
                "success": True,
                "message": "successfully create",
                "result": serializer.data,
            }
        )


class RetriveView(RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = self.serializer_class(post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                "success": True,
                "message": "successfuly edit",
                "code": status.HTTP_200_OK,
                "result": serializer.data,
            }
        )

    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()
        return Response(
            {
                "success": True,
                "message": "ochirildi ",
                "code": status.HTTP_204_NO_CONTENT,
            }
        )


class CommentListCreateView(ListCreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticated]
    queryset = PostComment.objects.all()


    def perform_create(self, serializer):
        serializer.save(author = self.request.user)
                
