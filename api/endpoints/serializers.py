from rest_framework import serializers

from core.models import JobModel
from endpoints.models import Customer

class StatusEnumSerailizer(serializers.Serializer):
    status = serializers.ChoiceField(choices=JobModel.STATE_CHOICES)

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        exclude = ["id", "created_at"]