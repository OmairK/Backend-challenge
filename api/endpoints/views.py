from datetime import datetime as dt
from typing import Optional

from django.shortcuts import render
from django.core import serializers
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

from core.models import JobModel
from core.tasks import query_to_csv
from core.utils.datetime import date_to_datetime
from endpoints.models import Customer, FileModel
from endpoints.serializers import StatusEnumSerailizer, CustomerSerializer


# TODO: Implement job status update logic at the model level
REVOKED_ACCEPTED = [JobModel.STARTED, JobModel.PAUSED, JobModel.CREATED]
PAUSED_ACCEPTED = [JobModel.STARTED]
RESUME_ACCEPTED = [JobModel.PAUSED]


@api_view(http_method_names=["GET"])
def generate_job_id(request):
    """
    View which generates a job id to manipulate an upload task
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


@api_view(http_method_names=["GET", "POST"])
@csrf_exempt
def task_status(
    request, job_id: Optional[str] = None,
):
    """
    View which checks/changes the status of a job
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
                    err = f"Job with job_id {job_id} is already revoked or completed"
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

    elif request.method == "GET":
        pass

    return Response(
        status=status.HTTP_200_OK,
        data={"job_id": job_id, "job_status": job.get_job_status_display()},
    )


@api_view(http_method_names=["POST"])
def file_upload_view(request):
    """
    View which hanldes the file upload
    """
    try:
        job_id = request.GET["job_id"]
    except KeyError:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error_message": "job_id not passed as a query_dict"})
    try:
        job = JobModel.objects.get(job_id=job_id)
    except JobModel.DoesNotExist:
        return Response(
            status=status.HTTP_404_NOT_FOUND,
            data={"error_message": f"Job with id {job_id} not found"},
        )
    try:
        file = FileModel.objects.create(__file=request.FILES)
    except Exception as err:
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"error_message": str(err.message)})
    
    return Response(status=status.HTTP_200_OK, data={"file": f"{file}"})
    


@api_view(http_method_names=["GET"])
def file_export_view(request):
    """
    View that handles the query request 
    and exports the result into a csv file 
    """
    try:

        date_gte = date_to_datetime(request.GET["date_gte"])
        date_lte = date_to_datetime(request.GET["date_lte"])
    except ValueError as err:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error_message": str(err.message)},
        )
    field_names = [field.name for field in Customer._meta.local_fields if field.name != "id" and field.name != "created_at"]
    query = Customer.objects.filter(created_at__range=(date_gte, date_lte)).values(
        *field_names
    )[:100]
    qs = CustomerSerializer( query,many=True)
    job = JobModel.objects.create()
    celery_task = query_to_csv.delay(job_id=job.job_id, fieldnames=field_names, query=qs.data)
    response = {
        "job_id": job.job_id,
        "job_message": f"Export job {job.get_job_status_display()}",
        "ref": {"url": f"job/{job.job_id}"},
    }
    return Response(status=status.HTTP_200_OK, data=response)
