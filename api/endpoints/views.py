from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
# Create your views here.

@api_view(http_method_names=['GET'])
def generate_job_id(request):
    """
    View which generates a job id to manipulate an upload task
    """
    pass

@api_view(http_method_names=['GET'])
def change_task_status(request, job_id, task_id, status):
    """
    View which changes the status of an ongoing/paused task 
    """
    if status == "REVOKE":
        pass
    elif status == "RESUME":
        pass
    elif status == "PAUSE":
        pass



class FileUploadView(GenericAPIView):
    """
    View which hanldes the file upload
    """
    pass


@api_view(http_method)
def file_export(request):
    pass