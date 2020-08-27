import uuid

from django.db import models

from core.utils.base_model import BaseModel


class JobModel(BaseModel):
    """Model to handle the status of jobs"""

    CREATED = "E"
    STARTED = "S"
    PAUSED = "P"
    RESUMED = "R"
    REVOKED = "Z"
    COMPLETED = "C"

    STATE_CHOICES = (
        (CREATED, "CREATED"),
        (STARTED, "STARTED"),
        (PAUSED, "PAUSED"),
        (RESUMED, "RESUMED"),
        (REVOKED, "REVOKED"),
        (COMPLETED, "COMPLETED"),
    )

    job_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    task_id = models.UUIDField(
        null=True
    )  # Stores the celery task id if it a clery_binded job
    job_status = models.CharField(
        choices=STATE_CHOICES, max_length=1, default=STATE_CHOICES[0][0]
    )
    celery_binded = models.BooleanField(default=False)

    def __str__(self):
        if self.celery_binded:
            return f"job_id: {self.task_type} task_id: {self.task_id} state: {self.get_job_status_display()}"
        return f"job_id: {self.job_id} state: {self.get_job_status_display()}"
