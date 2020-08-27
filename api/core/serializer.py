from rest_framework import serializers

from .models import JobModel


class JobSerializer(serializers.ModelSerializer):
    """
    Serializer to handle the task instances
    """

    class Meta:
        model = JobModel
        fields = "__all__"


# class ResponseSerializer(serializer.Serializer):
#
