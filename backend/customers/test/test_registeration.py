import pytest
from rest_framework.test import APIClient
from customers.models import Customers

@pytest.mark.django_db
def test_register_creates_customer():
    client = APIClient()

    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "monthly_income": 50000,
        "phone_number": "9999999999"
    }

    response = client.post("/register", payload, format="json")

    assert response.status_code in [200, 201]
    assert Customers.objects.count() == 1

    customer = Customers.objects.first()
    assert customer.monthly_income == 50000
    assert customer.age == 30
    assert customer.phone_number == "9999999999"
    assert customer.first_name == "John"
    assert customer.last_name == "Doe"
    
