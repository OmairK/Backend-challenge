import factory
from datetime import timezone, timedelta

from .models import Customer

class CustomerFactory(factory.django.DjangoModelFactory):
    """
    Factory to generate 
    """

    first_name = factory.Faker('name')
    last_name = factory.Faker('name')
    address = factory.Faker('street_address')
    email = factory.Faker('email')
    age = factory.Faker('pyint', min_value=10, max_value=99)
    company = factory.Faker('company')
    created_at = factory.Faker('date_time_this_decade', tzinfo=timezone(timedelta(minutes=0)))
    
    class Meta:
        model = Customer