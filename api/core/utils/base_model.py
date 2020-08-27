from django.db import models


class BaseModel(models.Model):
    """
    Base model from which all the models should inherit from
    """

    created_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True
