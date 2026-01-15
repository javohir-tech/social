from django.shortcuts import render
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
)
from rest_framework.views import APIView
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
from django.shortcuts import get_object_or_404


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


class PostCommentView(ListAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        post_id = self.kwargs["pk"]
        return PostComment.objects.filter(post__id=post_id)


class CommentListCreateView(ListCreateAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticated]
    queryset = PostComment.objects.all()
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentRetriveView(RetrieveAPIView):
    serializer_class = PostCommentSerializer
    permission_classes = [AllowAny]
    queryset = PostComment.objects.all()


class PostLikesView(ListAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        post_id = self.kwargs["pk"]

        return PostLike.objects.filter(post__id=post_id)


class CommentLikeList(ListAPIView):
    serializer_class = CommentLikeSerializer
    permission_classes = [AllowAny]
    pagination_class = CustomPagination

    def get_queryset(self):
        comment_id = self.kwargs["pk"]
        return CommentLike.objects.filter(comment__id=comment_id)


class PostLikeView(APIView):

    def post(self, request, pk):
        try:
            post = get_object_or_404(Post, id=pk)
            post_like = PostLike.objects.create(author=self.request.user, post=post)
            serializer = PostLikeSerializer(post_like)

            return Response(
                {
                    "success": True,
                    "message": "like successfuly ",
                    "data": serializer.data,
                }
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"{e}",
                }
            )

    def delete(self, request, pk):
        try:
            post = get_object_or_404(Post, id=pk)
            PostLike.objects.filter(author=self.request.user, post=post).delete()

            return Response({"success": True, "message": "dislike qilindi"})
        except Exception as e:
            return Response({"success": False, "message": f"{e} ochirilmadi"})


class CommentLikeView(APIView):

    def post(self, request, pk):
        try:
            comment = get_object_or_404(PostComment, id=pk)
            comment_like = CommentLike.objects.create(
                author=self.request.user, comment=comment
            )

            serializer = CommentLikeSerializer(comment_like)

            return Response(
                {"success": True, "message": "like bosildi ", "data": serializer.data}
            )
        except Exception as e:
            return Response({"success": False, "message": f"{e}"})

    def delete(self, request, pk):
        try:
            comment = get_object_or_404(PostComment, id=pk)
            CommentLike.objects.filter(
                author=self.request.user, comment=comment
            ).first().delete()

            return Response(
                {
                    "success": True,
                    "message": "dislike qilindi",
                }
            )
        except Exception as e:
            return Response({"success": False, "message": f"{e}"})
