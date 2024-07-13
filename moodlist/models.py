from django.db import models

# Create your models here.
class Mood(models.Model):
    mood = models.CharField(max_length=50)

    def __str__(self):
        return self.mood

class SpotifyToken(models.Model):
    user = models.CharField(max_length=50)
    access_token = models.CharField(max_length=200)
    refresh_token = models.CharField(max_length=200)
    token_type = models.CharField(max_length=50)
    expires_in = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user