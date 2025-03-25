from django.db import models

# Create your models here.
class ChatMessage(models.Model):
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)  # Auto timestamp

    def __str__(self):
        return f"{self.title} - {self.timestamp}"
