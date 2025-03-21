from django.db import models
import os

# Create your models here.
class Case(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.URLField()
    image = models.ImageField(upload_to='static/case_images/')
    status = models.CharField(max_length=100,default="Pending")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        """Delete the image file when the case is deleted"""
        if self.image:  # Ensure there is an image
            if os.path.isfile(self.image.path):  # Check if file exists
                os.remove(self.image.path)  # Delete the file
        super().delete(*args, **kwargs)  # Delete the object


class CaseUpdate(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="updates")
    timestamp = models.DateTimeField(auto_now_add=True)  # Auto stores update time
    title = models.CharField(max_length=100)
    location = models.URLField(blank=True, null=True)  # Optional URL
    description = models.TextField()
    image = models.ImageField(upload_to='static/case_images/', blank=True, null=True)  # Optional image

    def __str__(self):
        return f"Update for {self.case.title} on {self.timestamp}"
    
    def delete(self, *args, **kwargs):
        """Delete the image file when the update is deleted"""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)