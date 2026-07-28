from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# create Model data using python code -> each types of data is going to have a table in the data base by migration 
class Post(models.Model):
    title = models.CharField(max_length=75)
    body = models.TextField() # text input
    slug = models.SlugField()
    date = models.DateTimeField(auto_now_add=True)
    banner = models.ImageField(default='fallback.png', blank=True )
    explainer = models.ImageField(default='fallback.png', blank=True )
    author = models.ForeignKey(User, on_delete = models.CASCADE, default=None) ## handle the data in database

    def __str__(self):
        return self.title