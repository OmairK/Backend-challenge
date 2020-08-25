from django.urls import path

from endpoints.views import (
    file_export_view, file_upload_view,
    generate_job_id, task_status
)

urlpatterns = [
    path("export/", file_export_view, name="file_export"),
    path("task-status/<str:job_id>/", task_status, name="task_status"),
    path("new-job/", generate_job_id, name="new_job"),
    path("upload/", file_upload_view, name="resume"),
]
