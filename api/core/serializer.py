from rest_framework import serializers

from .models import TaskModel

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer to handle the task instances
    """
    class Meta:
        model = TaskModel
        fields = "__all__"