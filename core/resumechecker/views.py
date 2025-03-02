from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import JobDescription, Resume
from .serializer import JobDescriptionModelSerializer, ResumeModelSerializer
from .analyzer import process_resume

class JobDescriptionAPI(APIView):
     def get(self,request):
          queryset = JobDescription.objects.all()
          serializer = JobDescriptionModelSerializer(queryset, many=True)
          return Response(
               {
                    'status':True,
                    'data': serializer.data,
               }
          )

class AnalyzeResumeAPI(APIView):
     def post(self, request):
          try:
               data = request.data
               if not data.get('job_description'):
                    return Response(
                         {
                              'status':False,
                              'message':'job desctiption is required',
                              'data':{}
                         }
                    )
               serializer = ResumeModelSerializer(data=data)
               if not serializer.is_valid():
                    return Response(
                         {
                              'status':False,
                              'message':'errors',
                              'data':serializer.errors,
                         })
               
               serializer.save()
               _data = serializer.data
               resume_instance = Resume.objects.get(id=_data["id"])
               resume_path = resume_instance.resume.path
               print(resume_path)
               job_description = request.data.get('job_description')
               result = process_resume(resume_path,job_description)
               return Response(
                         {
                              'status':True,
                              'message':'Resume analyzed',
                              'data':result,
                         })

            
          except Exception as e:
               print(e)
               return Response(
                         {
                              'status':False,
                              'message':'Excetption occured',
                              'data':False,
                         })
          
