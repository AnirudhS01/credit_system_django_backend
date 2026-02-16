from django.urls import path
from .views import LoanEligibility , CreateLoan, ViewLoanbyId


urlpatterns = [
    path("check-eligibility/", LoanEligibility.as_view()),
    path("create-loan/", CreateLoan.as_view()),
    path("view-loan/<int:loan_id>", ViewLoanbyId.as_view())
]