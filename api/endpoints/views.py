from datetime import datetime as dt
from typing import Optional

from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from core.models import JobModel
from core.utils.file.export_handler import query_to_csv
from core.utils.datetime import date_to_datetime
from endpoints.models import Customer

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
            "job_status": job.job_status,
            "ref": {"url": f"upload?job_id={job.job_id}"},
        },
    )


@api_view(http_method_names=["GET", "POST"])
def task_status(
    request, job_id: Optional(str) = None,
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
        if request.data["status"] == "REVOKE":
            if JobModel.job_status not in REVOKED_ACCEPTED:
                err = f"Job with job_id {job_id} already revoked or completed"
        elif request.data["status"] == "RESUME":
            if JobModel.job_status not in RESUME_ACCEPTED:
                err = f"Job with job_id {job_id} is not paused"
        elif request.data["status"] == "PAUSE":
            if JobModel.job_status not in PAUSED_ACCEPTED:
                err = f"Job with job_id {job_id} is already revoked or completed"
        else:
            err = "Allowed status REVOKE, RESUME, PAUSE"

        if err is not None:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"error_message": err}
            )

        job.job_status = request.data["status"]
        job.save()

    elif request.method == "GET":
        pass

    return Response(
        status=status.HTTP_200_OK,
        data={"job_id": job_id, "job_status": job.job_status},
    )


@api_view(http_method_names=["POST"])
def file_upload_view(request, job_id):
    """
    View which hanldes the file upload
    """
    try:
        job = JobModel.objects.get(job_id=job_id)
    except JobModel.DoesNotExist:
        return Response(
            status=status.HTTP_404_NOT_FOUND,
            data={"error_message": f"Job with id {job_id} not found"},
        )


@api_view(http_method_names=["GET"])
def file_export_view(request, date_gte, date_lte):
    """
    View that handles the query request 
    and exports the result into a csv file 
    """
    try:
        date_gte = date_to_datetime(date_gte)
        date_lte = date_to_datetime(date_lte)
    except ValueError as err:
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={"error_message": str(err.message)},
        )

    field_names = [field for field in Customer._meta.get_all_field_names().remove("id")]
    query = Customer.objects.filter(created_at__range=(date_gte, date_lte)).values(
        *field_names
    )
    job = JobModel.objects.create()
    celery_task = query_to_csv.delay(job.job_id, field_names, query)
    response = {
        "job_id": job.job_id,
        "job_message": "Export job started",
        "ref": {"url": f"job/{job.job_id}"},
    }
    return Response(status=status.HTTP_200_OK, data=response)
