from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Blog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_blog')
    headline = models.CharField(max_length=50)

    def get_absolute_url(self):
        pass

    def __str__(self):
        return self.id


class Entry(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    body = models.TextField()
