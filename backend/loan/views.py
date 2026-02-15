
from django.shortcuts import render
from customers.models import Customers
from rest_framework.response import Response
from .serializers import LoanEligibilitySerializer
from rest_framework.views import APIView
from rest_framework import status
from .services import calculate_credit_score , correct_interest, calculate_emi
from .models import Loan
from django.utils.timezone import now
from django.db.models import Sum
from decimal import Decimal

class LoanEligibility(APIView):

    def post(self, request):
        serializer = LoanEligibilitySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        customer_id = serializer.validated_data["customer_id"]
        loan_amount = serializer.validated_data["loan_amount"]
        interest_rate = serializer.validated_data["interest_rate"]
        tenure = serializer.validated_data["tenure"]

        try:
            customer = Customers.objects.get(id=customer_id)
        except Customers.DoesNotExist:
            return Response({"error": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        credit_score = calculate_credit_score(customer_id, loan_amount)

        corrected_interest = correct_interest(credit_score, interest_rate)

        if corrected_interest is None:
            approval = False
            monthly_installment = None
        else:
            monthly_installment = calculate_emi(
                loan_amount,
                corrected_interest,
                tenure
            )

            current_emi_total = customer.loans.filter(
                end_date__gte=now().date()
            ).aggregate(total=Sum("monthly_payment"))["total"] or Decimal("0")

            if current_emi_total + monthly_installment > (customer.monthly_salary * Decimal("0.5")):
                approval = False
            else:
                approval = True

        return Response(
            {
                "customer_id": customer_id,
                "approval": approval,
                "interest_rate": interest_rate,
                "corrected_interest_rate": corrected_interest,
                "tenure": tenure,
                "monthly_installment": monthly_installment,
            },
            status=status.HTTP_200_OK,
        )