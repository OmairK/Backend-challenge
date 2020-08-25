from django.db import models
from core.utils.base_model import BaseModel


class Customer(BaseModel):
    """Model to handle customer data"""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    age = models.IntegerField()
    company = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} from {self.company}"

