from django.db import models

# Create your models here.

class Resume(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    resume = models.FileField(upload_to="resume")

class JobDescription(models.Model):
    job_title = models.CharField(max_length=100)
    job_description = models.TextField()

    def __str__(self):
        return self.job_title
    
class ChatHistory(models.Model):
    user_message = models.TextField()
    ai_response = models.TextField()
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)