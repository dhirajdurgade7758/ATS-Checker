from django.contrib import admin
from .models import Resume, JobDescription,ChatHistory

# Register your models here.
admin.site.register(Resume)
admin.site.register(JobDescription)
admin.site.register(ChatHistory)