from django.urls import path
from .views import LoanEligibility


urlpatterns = [
    path("check-eligibility/", LoanEligibility.as_view())
]