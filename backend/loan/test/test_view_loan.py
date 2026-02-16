import pytest
from rest_framework.test import APIClient
from customers.models import Customers
from loan.models import Loan
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

@pytest.mark.django_db
def test_view_loan_details():
    client = APIClient()
    
    # Setup data
    customer = Customers.objects.create(
        first_name="Test", last_name="User", age=30, monthly_salary=50000, 
        phone_number="1234567890", approved_limit=1000000
    )
    
    start_date = now().date()
    loan = Loan.objects.create(
        customer=customer,
        loan_amount=20000,
        tenure=12,
        interest_rate=12,
        monthly_payment=1800,
        no_emi_paid_on_time=0,
        start_date=start_date,
        end_date=start_date + relativedelta(months=12)
    )

    response = client.get(f"/api/view-loan/{loan.id}")

    assert response.status_code == 200
    assert response.data["loan_id"] == loan.id
    assert response.data["customer"]["id"] == customer.id
    assert response.data["loan_amount"] == 20000

@pytest.mark.django_db
def test_view_loan_not_found():
    client = APIClient()
    response = client.get("/api/view-loan/9999")
    assert response.status_code == 404
