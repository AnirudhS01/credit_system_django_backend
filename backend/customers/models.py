# in the doc they have asked about current debt but that is a derived data 
# so its better to calculate it , better storage efficiency

from django.db import models

class Customers(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField(blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2)
    approved_limit = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return f"{self.first_name} {self.last_name}" 
    

