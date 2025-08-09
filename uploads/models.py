from django.db import models
from django.contrib.auth.models import User
import os

class FileUpload(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    filename = models.CharField(max_length=255)
    upload_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    word_count = models.PositiveIntegerField(default=0)
    file_size = models.PositiveIntegerField(default=0)  # in bytes
    file_type = models.CharField(max_length=10, default='')

    class Meta:
        ordering = ['-upload_time']

    def __str__(self):
        return f"{self.filename} ({self.user.username})"

    def get_file_size_display(self):
        """Convert bytes to human readable format"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.1f} MB"

    def save(self, *args, **kwargs):
        if self.file:
            self.filename = os.path.basename(self.file.name)
            self.file_size = self.file.size
            self.file_type = os.path.splitext(self.filename)[1].lower()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete file from storage when model is deleted"""
        if self.file:
            # Delete physical file
            try:
                if os.path.isfile(self.file.path):
                    os.remove(self.file.path)
            except Exception as e:
                print(f"Error deleting file {self.file.path}: {e}")
        
        super().delete(*args, **kwargs)


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.action}"