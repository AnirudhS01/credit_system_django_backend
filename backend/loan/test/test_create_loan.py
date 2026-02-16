import pytest
from rest_framework.test import APIClient
from customers.models import Customers
from loan.models import Loan

@pytest.mark.django_db
def test_create_loan_success():
    client = APIClient()
    
    # Create a creditworthy customer
    customer = Customers.objects.create(
        first_name="Rich",
        last_name="Richie",
        age=30,
        monthly_salary=100000,
        phone_number="1234567890",
        approved_limit=3600000 
    )

    payload = {
        "customer_id": customer.id,
        "loan_amount": 50000,
        "interest_rate": 10,
        "tenure": 12
    }

    response = client.post("/api/create-loan/", payload, format="json")

    assert response.status_code == 201
    assert response.data["loan_approved"] is True
    assert response.data["loan_id"] is not None
    
    # Verify DB persistence
    assert Loan.objects.count() == 1
    loan = Loan.objects.first()
    assert loan.customer == customer
    assert loan.loan_amount == 50000

@pytest.mark.django_db
def test_create_loan_customer_not_found():
    client = APIClient()
    
    payload = {
        "customer_id": 99999, # Non-existent ID
        "loan_amount": 50000,
        "interest_rate": 10,
        "tenure": 12
    }

    response = client.post("/api/create-loan/", payload, format="json")

    assert response.status_code == 404
    assert response.data["error"] == "Customer not found"
