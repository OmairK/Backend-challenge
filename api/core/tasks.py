import csv
import time
import os
from typing import List

from celery.exceptions import TimeoutError, TaskRevokedError
from celery.contrib import rdb

from django.forms.models import model_to_dict
from django.conf import settings
from core.models import JobModel
from api import celery_app


@celery_app.task(bind=True)
def query_to_csv(self, job_id: str, fieldnames: List[str], query):
    """
    Function for handling async csv export by binding it to the relevant job
    """
    job = JobModel.objects.get(job_id=job_id)
    job.job_status = JobModel.STARTED
    job.celery_binded = True
    job.task_id = self.request.id
    job.save()
    csvfile = open(f"./exported_csv/{job_id}.csv", "w", newline="")

    csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    csvwriter.writeheader()
    for row in query:
        time.sleep(3)
        job = JobModel.objects.get(job_id=job_id)
        if job.job_status == JobModel.STARTED or job.job_status == JobModel.RESUMED:
            csvwriter.writerow(row)

        if job.job_status == JobModel.REVOKED:
            csvfile.close()
            os.remove(f"./exported_csv/{job_id}.csv")
            raise TaskRevokedError

        elif job.job_status == JobModel.PAUSED:
            pulse_try = 0
            while (
                job.job_status == JobModel.PAUSED
                and pulse_try <= settings.PULSE_MAX_TRIES
            ):
                pulse_try += 1
                time.sleep(settings.PAUSE_PULSE)
                job = JobModel.objects.get(job_id=job_id)
            if pulse_try == settings.PULSE_MAX_TRIES:
                job.task_status = JobModel.REVOKED
                job.save()
            elif job.job_status == JobModel.RESUMED:
                csvwriter.writerow(row)

    csvfile.close()
    job.job_status = JobModel.COMPLETED
    job.save()
    return "Job Completed"
