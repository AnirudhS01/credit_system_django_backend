from django.urls import path
from .views import LoanEligibility , CreateLoan


urlpatterns = [
    path("check-eligibility/", LoanEligibility.as_view()),
    path("create-loan/", CreateLoan.as_view())
]