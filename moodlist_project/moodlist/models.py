from django.db import models

# Create your models here.
class Mood(models.Model):
    mood = models.CharField(max_length=50)

    def __str__(self):
        return self.mood