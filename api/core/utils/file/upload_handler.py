import time

from django.core.files.uploadhandler import FileUploadHandler, StopUpload
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.conf import settings

from core.models import JobModel


class CustomFileUploadHandler(FileUploadHandler):
    """
    Custom file upload handler which handles the file upload as 
    job and can be stopped midway if the job is revoked.
    Acts mainly as a TemporaryFileUpload with additional logic.
    """

    # TODO:Logging file progress
    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.file = TemporaryUploadedFile(
            self.file_name, self.content_type, 0, self.charset, self.content_type_extra
        )
        job = JobModel.objects.get(job_id=self.request.GET["job_id"])
        job.job_status = JobModel.STARTED
        job.save()

    def receive_data_chunk(self, raw_data, start):
        # Depending on the job id the task handling will stop
        # midway if the status is 'REVOKED'
        time.sleep(0.5)
        try:
            job = JobModel.objects.get(job_id=self.request.GET["job_id"])
            print(job)
        except JobModel.DoesNotExist:
            raise StopUpload(connection_reset=True)

        if job.job_status == JobModel.PAUSED:
            pulse_try = 0
            while (
                job.job_status == JobModel.PAUSED
                and pulse_try <= settings.PULSE_MAX_TRIES
            ):
                pulse_try += 1
                time.sleep(settings.PAUSE_PULSE)
                job = JobModel.objects.get(job_id=self.request.GET["job_id"])
            if pulse_try == settings.PULSE_MAX_TRIES:
                job.delete()
                job.save()
                raise StopUpload(connection_reset=True)
        elif job.job_status == JobModel.REVOKED:
            job.delete()
            raise StopUpload(connection_reset=True)

        self.file.write(raw_data)

    def file_complete(self, file_size):
        # delete the job after completion
        job = JobModel.objects.get(job_id=self.request.GET["job_id"])
        job.delete()
        self.file.seek(0)
        self.file.size = file_size
        return self.file
