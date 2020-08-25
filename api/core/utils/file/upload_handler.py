import time

from django.core.files.uploadhandler import FileUploadHandler, StopUpload
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.conf import settings

from core.models import JobModel


class CustomFileUploadHandler(FileUploadHandler):
    """
    Custom file upload handler which handles the file upload as 
    job and could be stopped midway if the job is revoked.
    Acts mainly as a TemporaryFileUpload with additional logic.
    """

    # TODO:Logging file progress
    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.file = TemporaryUploadedFile(
            self.file_name, self.content_type, 0, self.charset, self.content_type_extra
        )

    def receive_data_chunk(self, raw_data, start):
        # Depending on the job id the task handling will stop
        # midway if the status is 'REVOKED'
        job = JobModel.get(job_id=self.request.GET("job_id"))
        if job.job_status == JobModel.CREATED:
            pass
        elif job.job_status == JobModel.STARTED:
            pass
        elif job.job_status == JobModel.PAUSED:
            pulse_try = 0
            while (
                job.job_status == JobModel.PAUSED
                and pulse_try <= settings.PULSE_MAX_TRIES
            ):
                pulse_try += 1
                time.sleep(settings.PAUSE_PULSE)
            if pulse_try == settings.PULSE_MAX_TRIES:
                job.task_status = JobModel.REVOKED
                job.save()

                raise StopUpload(connection_reset=True)
        elif job.job_status == JobModel.REVOKED:
            raise StopUpload(connection_reset=True)

        self.file.write(raw_data)

    def file_complete(self, file_size):
        # change the job status to completed for a sucessful job

        job = JobModel.get(job_id=self.request.GET("job_id"))
        job.job_status == JobModel.COMPLETED
        job.save()
        self.file.seek(0)
        self.file.size = file_size
        return self.file
