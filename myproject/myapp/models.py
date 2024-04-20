from django.db import models
from django.contrib.auth.models import User

class Image(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    upload_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='images/')
    filters = models.ManyToManyField('Filter')

class Filter(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='icons/')

class Effect(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='icons/')

class Frame(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='icons/')

class Typography(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    font_family = models.CharField(max_length=100)
    font_size = models.PositiveIntegerField()
    font_color = models.CharField(max_length=7)  # Assuming hex color code


