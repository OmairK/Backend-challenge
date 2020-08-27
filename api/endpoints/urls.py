from django.urls import path

from .views import generate_job_id, FileUploadView, FileExportView, JobStatusView

urlpatterns = [
    path("export/", FileExportView.as_view(), name="file_export"),
    path("job-status/<str:job_id>/", JobStatusView.as_view(), name="job_status"),
    path("new-job/", generate_job_id, name="new_job"),
    path("upload/", FileUploadView.as_view(), name="upload"),
]
