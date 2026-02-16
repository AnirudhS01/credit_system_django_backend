import pytest
from rest_framework.test import APIClient
from customers.models import Customers

@pytest.mark.django_db
def test_check_eligibility_approved():
    client = APIClient()
    
    # Create a customer with high income to ensure eligibility
    customer = Customers.objects.create(
        first_name="Test",
        last_name="User",
        age=25,
        monthly_salary=50000,
        phone_number="1234567890",
        approved_limit=5000000 # High limit
    )

    payload = {
        "customer_id": customer.id,
        "loan_amount": 10000,
        "interest_rate": 12,
        "tenure": 12
    }

    response = client.post("/api/check-eligibility/", payload, format="json")

    assert response.status_code == 200
    assert response.data["customer_id"] == customer.id
    assert response.data["approval"] is True
    assert "corrected_interest_rate" in response.data
    assert "monthly_installment" in response.data

@pytest.mark.django_db
def test_check_eligibility_rejected_high_amount():
    client = APIClient()
    
    # Create a customer with low limit
    customer = Customers.objects.create(
        first_name="Test",
        last_name="User",
        age=25,
        monthly_salary=10000,
        phone_number="1234567890",
        approved_limit=5000 
    )

    # Request loan higher than limit
    payload = {
        "customer_id": customer.id,
        "loan_amount": 50000,
        "interest_rate": 12,
        "tenure": 12
    }

    response = client.post("/api/check-eligibility/", payload, format="json")
    
    assert response.status_code == 200
    assert response.data["customer_id"] == customer.id
    assert "approval" in response.data
