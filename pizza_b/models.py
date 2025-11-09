from django.db import models

# Create your models here.

class Pizza(models.Model):
    name = models.TextField()
    type = models.TextField()
    cost = models.FloatField()
    description = models.TextField()
    # ingredients = for the future, perhaps for searching
