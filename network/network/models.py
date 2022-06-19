from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime

class User(AbstractUser):
    follow_list = models.ManyToManyField("self", related_name='follows', blank=True, symmetrical=False)

    def get_follower_count(self):
        return User.objects.filter(follow_list=self).count()
    
    def get_following_count(self):
        return self.follow_list.count()
    

class Post(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="userID")
    contents = models.CharField(max_length=280, default=None)
    created_dt = models.DateTimeField(default=datetime.datetime.now)
    likes = models.ManyToManyField(User, related_name="likes", blank=True)

    def __str__ (self):
        return f"{self.id}: {self.contents} by {self.user_id} on {self.created_dt}"
    
    def get_likes_count(self):
        return self.likes.count()

