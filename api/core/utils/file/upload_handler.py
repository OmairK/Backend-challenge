from django.core.files.uploadhandler import FileUploadHandler, StopUpload
from django.core.files.uploadedfile import TemporaryUploadedFile

from core.models import TaskModel

class CustomFileUploadHandler(FileUploadHandler):
    #TODO:Logging file
    def new_file(self, *args, **kwargs):
        super().new_file(*args, **kwargs)
        self.file = TemporaryUploadedFile(self.file_name, self.content_type, 0, self.charset, self.content_type_extra)
        
    def receive_data_chunk(self, raw_data, start):
        # Depending on the job id the task handling will stop
        # midway if the status is 'REVOKED'
        if TaskModel.get(job_id=self.request.GET()).task_status == TaskModel.STARTED:
            self.file.write(raw_data)
        else:
            raise StopUpload(connection_reset=True)
    
    def file_complete(self, file_size):
        self.file.seek(0)
        self.file.size = file_size
        return self.file
        