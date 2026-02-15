from django.db import models

class Loan(models.Model):
    customer_id = models.ForeignKey("customers.Customers", on_delete=models.CASCADE, related_name="loans")
    # loan id i think will be auto generated , based on the table it is likely
    loan_amount = models.DecimalField(max_digits=15, decimal_places=2)
    tenure = models.IntegerField() # assuming it is months
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=15, decimal_places=2)
    no_emi_paid_on_time = models.IntegerField()
    start_date = models.DateField() 
    end_date = models.DateField()  # derived field , we acn calcuale based on emi

    def __str__(self):
        return f"Loan {self.id}"

# this works for a preexisting customer , but what if he is new ? yea this table row is created only when
# a loan is created so it handles both , 
