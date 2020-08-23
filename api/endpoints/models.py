from django.db import models

class Customer(models.Model):
    """Model to handle customer data"""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact_number = models.PhoneNumberField()
    age = models.IntegerField()
    company = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} from {self.company}"

