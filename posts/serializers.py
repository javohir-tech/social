from rest_framework import serializers
from users.models import User
from .models import Post , PostLike


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "photo"]


class PostSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    author = UserSerializer()
    like_count = serializers.SerializerMethodField("post_like_count")
    comment_count = serializers.SerializerMethodField("post_comment_count")
    me_liked = serializers.SerializerMethodField('get_me_liked')

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "image",
            "caption",
            "created_time",
            "like_count",
            "comment_count",
            "me_liked",
        ]

    def post_like_count(self, obj):
        return obj.likes.count()

    def post_comment_count(self, obj):
        return obj.comments.count()
    
    def get_me_liked(self , obj):
        request = self.context.get('request' , None)
        
        if request and request.user.is_authenticated :
            try :
                like = PostLike.objects.get(author = request , post = obj)
                return True
            except Post.DoesNotExist :
                return False
        
        return True
            
        
