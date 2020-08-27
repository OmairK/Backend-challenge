from datetime import datetime as dt
from typing import Optional

from django.core import serializers
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from django.views.decorators.csrf import csrf_exempt

from core.models import JobModel
from core.tasks import query_to_csv
from core.utils.datetime import date_to_datetime
from endpoints.models import Customer, FileModel
from endpoints.serializers import CustomerSerializer

# TODO: Implement job status update logic at the model level
REVOKED_ACCEPTED = [JobModel.STARTED, JobModel.PAUSED, JobModel.CREATED]
PAUSED_ACCEPTED = [JobModel.STARTED]
RESUME_ACCEPTED = [JobModel.PAUSED]


@api_view(http_method_names=["GET"])
def generate_job_id(request):
    """
    Generates a new job to manipulate an upload task.
    Export request generates its own job as it is implemented as an async task.
        
        # Example request
        import requests
        url = "http://localhost:8000/api/v1/new-job/"
        response = requests.request("GET", url)
    """
    job = JobModel.objects.create()
    return Response(
        status=status.HTTP_200_OK,
        data={
            "job_id": job.job_id,
            "job_status": job.get_job_status_display(),
            "ref": {"url": f"upload?job_id={job.job_id}"},
        },
    )


class JobStatusView(APIView):
    authentication_classes = []
    def post(self, request, job_id: Optional[str] = None, format=None):
        """
        View to change the status of the job

            import requests
            url = "http://localhost:8000/api/v1/job-status/<uuid>/"
            payload = {'status': 'PAUSE'}
            response = requests.request("POST", url, data=payload)
        """
        try:
            job = JobModel.objects.get(job_id=job_id)
        except JobModel.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"error_message": f"Job with id {job_id} not found"},
            )
        err = None
        if request.method == "POST":
            try:
                if request.data["status"] == "REVOKE":
                    if job.job_status not in REVOKED_ACCEPTED:
                        err = f"Job with job_id {job_id} already revoked or completed"
                    else:
                        job.job_status = JobModel.REVOKED
                elif request.data["status"] == "RESUME":
                    if job.job_status not in RESUME_ACCEPTED:
                        err = f"Job with job_id {job_id} is not paused"
                    else:
                        job.job_status = JobModel.RESUMED
                elif request.data["status"] == "PAUSE":
                    if job.job_status not in PAUSED_ACCEPTED:
                        err = (
                            f"Job with job_id {job_id} is already revoked or completed"
                        )
                    else:
                        job.job_status = JobModel.PAUSED
                else:
                    err = "Allowed status REVOKE, RESUME, PAUSE"
            except KeyError:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error_message": "'status' not present in request body"},
                )

            if err is not None:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST, data={"error_message": err}
                )

            job.save()
        return Response(
            status=status.HTTP_200_OK,
            data={"job_id": job_id, "job_status": job.get_job_status_display()},
        )

    def get(self, request, job_id: Optional[str] = None, format=None):
        """
        View to get the status of the job
            
            # Example request
            import requests
            url = "http://localhost:8000/api/v1/job-status/<uuid>"
            response = requests.request("GET", url)
        """
        try:
            job = JobModel.objects.get(job_id=job_id)
        except JobModel.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={"error_message": f"Job with id {job_id} not found"},
            )
        return Response(
            status=status.HTTP_200_OK,
            data={"job_id": job_id, "job_status": job.get_job_status_display()},
        )


class FileUploadView(APIView):
    """
    File upload handling view which passes the request data through 
    MultiPartParser -> CustomFileUploadHandler -> request

        import requests
        url = "http://localhost:8000/api/v1/upload/"
        querystring = {"job_id":"01c10aa0-cfe9-4ffb-bae9-9ca2b8f77a34"}
        file = {'file': open('temp.xls', 'rb')}
        response = requests.request("POST", url, data=payload, params=querystring)

    """

    parser_classes = [MultiPartParser]
    authentication_classes = []

    def post(self, request, format=None):
        try:
            job_id = request.GET["job_id"]
            job = JobModel.objects.get(job_id=job_id)
        except JobModel.DoesNotExist:
            return Response(
                status=404, data={"error_message": f"Job with id '{job_id}'' not found"}
            )
        try:
            files = request.FILES
            FileModel.objects.create(_file=files["file"])
            return Response(status=200, data={"file": files["file"].name})
        except Exception as err:
            if JobModel.objects.filter(job_id=job_id).exists():
                return Response(status=500)
            return Response(status=200, data={"error_message": "Job revoked"})


class FileExportView(APIView):
    authentication_classes = []
    def get(self, request, format=None):
        """
        View that handles the query request and exports the result into a csv file.


            import requests
            url = "http://localhost:8000/api/v1/export/"
            querystring = {"date_gte":"2011-02-02","date_lte":"2025-02-02"}
            response = requests.request("GET", url, params=querystring) 
        """
        try:

            date_gte = date_to_datetime(request.GET["date_gte"])
            date_lte = date_to_datetime(request.GET["date_lte"])
        except ValueError as err:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"error_message": str(err.message)},
            )
        field_names = [
            field.name
            for field in Customer._meta.local_fields
            if field.name != "id" and field.name != "created_at"
        ]
        query = Customer.objects.filter(created_at__range=(date_gte, date_lte)).values(
            *field_names
        )
        qs = CustomerSerializer(query, many=True)
        job = JobModel.objects.create()
        celery_task = query_to_csv.delay(
            job_id=job.job_id, fieldnames=field_names, query=qs.data
        )
        response = {
            "job_id": job.job_id,
            "job_message": f"Export job {job.get_job_status_display()}",
            "ref": {"url": f"job/{job.job_id}"},
        }
        return Response(status=status.HTTP_200_OK, data=response)
