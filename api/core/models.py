from django.db import models


class JobModel(models.Model):
    """Model to handle the status of jobs"""

    STARTED = "S"
    PAUSED = "P"
    RESUMED = "R"
    REVOKED = "Z"
    COMPLETED = "C"

    STATE_CHOICES = (
        (STARTED, "STARTED"),
        (PAUSED, "PAUSED"),
        (RESUMED, "RESUMED"),
        (REVOKED, "REVOKED"),
        (COMPLETED, "COMPLETED"),
    )

    job_id = models.UUIDField()  
    task_id = models.UUIDField()    # Stores the celery task id if it a clery_binded job
    task_status = models.CharField(
        choices=STATE_CHOICES, max_length=1, defautl=STATE_CHOICES[0][0]
    )
    celery_binded = models.BooleanField(default=True)

    def __str__(self):
        if self.celery_binded:
            return f"job_id: {self.task_type} task_id: {self.task_id} state: {self.get_task_status_display()}"
        return f"job_id: {self.job_id} state: {self.get_task_status_display()}"

    
