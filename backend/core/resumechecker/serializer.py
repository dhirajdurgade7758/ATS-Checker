from rest_framework import serializers
from .models import JobDescription, Resume

class JobDescriptionModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDescription
        fields ='__all__'

class ResumeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = '__all__'