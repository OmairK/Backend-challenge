# Generated by Django 3.1 on 2020-08-25 22:39

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JobModel",
            fields=[
                ("created_at", models.DateTimeField(auto_now=True)),
                (
                    "job_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("task_id", models.UUIDField()),
                (
                    "job_status",
                    models.CharField(
                        choices=[
                            ("E", "CREATED"),
                            ("S", "STARTED"),
                            ("P", "PAUSED"),
                            ("R", "RESUMED"),
                            ("Z", "REVOKED"),
                            ("C", "COMPLETED"),
                        ],
                        default="E",
                        max_length=1,
                    ),
                ),
                ("celery_binded", models.BooleanField(default=False)),
            ],
            options={"abstract": False,},
        ),
    ]
