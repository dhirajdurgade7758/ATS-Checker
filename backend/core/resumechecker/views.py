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
                    print("job description not found")
                    return Response(
                         {
                              'status':False,
                              'message':'job desctiption is required',
                              'data':{}
                         }
                    )
               serializer = ResumeModelSerializer(data=data)
               if not serializer.is_valid():
                    print("serializer not valid")
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
          


from rest_framework import status
from .models import Resume, ChatHistory
from .serializer import ResumeModelSerializer, ChatHistorySerializer
from .assistant import ResumeAssistant


from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status

class ResumeAssistantAPI(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def post(self, request):
        try:
            # Handle resume file upload
            if 'resume' in request.FILES:
                serializer = ResumeModelSerializer(data=request.data)
                if not serializer.is_valid():
                    return Response({
                        'status': False,
                        'message': 'Invalid resume data',
                        'data': serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                serializer.save()
                resume_instance = serializer.instance
                
                # Process the resume
                success = ResumeAssistant.load_resume(resume_instance,resume_instance.resume.path)
                if not success:
                    return Response({
                        'status': False,
                        'message': 'Failed to process resume',
                        'data': {}
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({
                    'status': True,
                    'message': 'Resume uploaded successfully',
                    'data': {
                        'resume_id': resume_instance.id,
                        'message': 'You can now chat about your resume'
                    }
                }, status=status.HTTP_201_CREATED)
            
            # Handle chat messages
            elif 'message' in request.data:
                if not hasattr(self, 'assistant') or not self.assistant.resume_text:
                    return Response({
                        'status': False,
                        'message': 'Please upload a resume first',
                        'data': {}
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                user_message = request.data.get('message')
                resume_id = request.data.get('resume_id')
                
                if not resume_id:
                    return Response({
                        'status': False,
                        'message': 'Resume ID is required',
                        'data': {}
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                response = self.assistant.chat(user_message)
                
                # Save chat history
                chat = ChatHistory.objects.create(
                    user_message=user_message,
                    ai_response=response.get('response', ''),
                    resume_id=resume_id
                )
                
                return Response({
                    'status': True,
                    'message': 'Response generated',
                    'data': {
                        'response': response.get('response'),
                        'chat_id': chat.id
                    }
                })
            
            else:
                return Response({
                    'status': False,
                    'message': 'Either resume file or message must be provided',
                    'data': {}
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e),
                'data': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ChatHistoryAPI(APIView):
    def get(self, request, resume_id):
        try:
            chats = ChatHistory.objects.filter(resume_id=resume_id).order_by('-created_at')
            serializer = ChatHistorySerializer(chats, many=True)
            return Response({
                'status': True,
                'message': 'Chat history retrieved',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'status': False,
                'message': str(e),
                'data': {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)