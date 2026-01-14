from django.contrib import admin
from posts.models import Post, PostComment, CommentLike, PostLike


class PostAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "caption", "created_time"]
    search_fields = ["author__username", "caption"]


class PostCommetAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "post", "comment", "created_time"]
    search_fields = ["author__username", "post__caption", "comment"]


class PostLikeAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "post", "created_time"]
    search_fields = ["author__username", "post__caption"]


class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ["id", "author", "comment", "created_time"]
    search_fields = ["author__username"]


admin.site.register(Post, PostAdmin)
admin.site.register(PostComment, PostCommetAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)


# Register your models here.
