from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Post, PostComment, PostLike, CommentLike
from .serializers import (
    PostSerializer,
    PostCommentSerializer,
    PostLikeSerializer,
    CommentLikeSerializer,
)
from shared.custom_pagiation import CustomPagination
from rest_framework.response import Response


class PostListView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Post.objects.all()


class CreatePostView(CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    # def perform_create(self, serializer):
    #     serializer.save(author= self.request.user)
    #     return Response({
    #         "success" : True,
    #         "message" :"Successfully create",
    #         "result" : serializer.data
    #     })
    
    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author = self.request.user)
        return Response(
            {
                'success' : True,
                "message" : "successfully create", 
                "result" : serializer.data
            }
        )


# Create your views here.
