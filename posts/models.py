from django.db import models
from django.contrib.auth import get_user_model
from shared.models import BaseModel
from django.core.validators import FileExtensionValidator , MaxLengthValidator
from django.db.models import UniqueConstraint , CheckConstraint, Q

User = get_user_model()


class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    image = models.FileField(
        validators=[FileExtensionValidator(allowed_extensions=["jpeg", "jpg", "png"])],
        upload_to='post_images' , 
    )
    caption = models.TextField(validators=[MaxLengthValidator(2000)])
    
    class Meta :
        db_table = 'post'
        verbose_name = 'post'
        verbose_name_plural = 'posts'
        
class PostComment(BaseModel) :
    author = models.ForeignKey(User , on_delete=models.CASCADE )
    post = models.ForeignKey(Post , on_delete=models.CASCADE ,  related_name='comments')
    comment = models.TextField(max_length=3000)
    parent = models.ForeignKey(
        'self' ,
        on_delete=models.CASCADE,
        related_name='child',
        null=True, 
        blank=True
    )
    
    
    
    def  __str__(self):
        return f"comment by {self.author}"
    
class PostLike(BaseModel) :
    author = models.ForeignKey(User , on_delete=models.CASCADE)
    post  = models.ForeignKey(Post , on_delete=models.CASCADE , related_name='likes')
    
    class Meta :
        constraints = [
            UniqueConstraint(
                fields = ['author' , 'post'], 
                name= 'unique  constraint post like'
            )
        ]

class CommentLike(BaseModel) :
    author = models.ForeignKey(User , on_delete=models.CASCADE )
    comment = models.ForeignKey(PostComment , on_delete=models.CASCADE )
    
    class Meta :
        constraints = [
            UniqueConstraint(
                fields=['author' , 'comment'],
                name= 'comment like unique'
            )
        ]   

