import pytest
from rest_framework.test import APIClient
from customers.models import Customers
from loan.models import Loan
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

@pytest.mark.django_db
def test_view_customer_loans():
    client = APIClient()
    
    # Setup data
    customer = Customers.objects.create(
        first_name="Test", last_name="User", age=30, monthly_salary=50000, 
        phone_number="1234567890", approved_limit=1000000
    )
    
    start_date = now().date()
    
    # Loan 1
    Loan.objects.create(
        customer=customer,
        loan_amount=20000,
        tenure=12,
        interest_rate=12,
        monthly_payment=1800,
        no_emi_paid_on_time=0,
        start_date=start_date,
        end_date=start_date + relativedelta(months=12)
    )
    
    # Loan 2
    Loan.objects.create(
        customer=customer,
        loan_amount=10000,
        tenure=6,
        interest_rate=10,
        monthly_payment=1700,
        no_emi_paid_on_time=0,
        start_date=start_date,
        end_date=start_date + relativedelta(months=6)
    )

    response = client.get(f"/api/view-loans/{customer.id}")

    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    
    # Check identifying details
    loan_amounts = [loan["loan_amount"] for loan in response.data]
    assert 20000 in loan_amounts
    assert 10000 in loan_amounts
    
    # Check structure
    first_loan = response.data[0]
    assert "repayments_left" in first_loan
    assert "interest_rate" in first_loan

@pytest.mark.django_db
def test_view_customer_loans_no_loans():
    client = APIClient()
    customer = Customers.objects.create(
        first_name="Empty", last_name="User", age=30, monthly_salary=50000, 
        phone_number="1111111111", approved_limit=1000000
    )
    
    response = client.get(f"/api/view-loans/{customer.id}")
    assert response.status_code == 200
    assert response.data == []
