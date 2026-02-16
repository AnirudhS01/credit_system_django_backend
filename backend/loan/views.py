
from django.shortcuts import render
from customers.models import Customers
from rest_framework.response import Response
from .serializers import LoanEligibilitySerializer
from rest_framework.views import APIView
from rest_framework import status
from .services import calculate_credit_score , correct_interest, calculate_emi, eligibility
from .models import Loan
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta

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

        approval , monthly_installment , corrected_interest, message = eligibility(customer_id , loan_amount,tenure , interest_rate)
        return Response(
            {
                "customer_id": customer_id,
                "approval": approval,
                "interest_rate": interest_rate,
                "corrected_interest_rate": corrected_interest,
                "tenure": tenure,
                "monthly_installment": monthly_installment,
                "message": message
            },
            status=status.HTTP_200_OK,
        )   


class CreateLoan(APIView):
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
        
        approval , monthly_installment , corrected_interest, message = eligibility(
            customer_id , 
            loan_amount,
            tenure , 
            interest_rate
        )

        if approval == False:
            return Response({
                "loan_id": None,
                "customer_id": customer_id,
                "loan_approved": False,
                "message": message,
                "monthly_installment": monthly_installment
            }, status=status.HTTP_200_OK)       
        
        start_date = now().date()
        end_date = start_date + relativedelta(months=tenure)
        
        loan = Loan.objects.create(
            customer=customer,
            loan_amount=loan_amount,
            tenure=tenure,
            interest_rate=corrected_interest,
            monthly_payment=monthly_installment,
            no_emi_paid_on_time=0,
            start_date=start_date,
            end_date=end_date
        )

        return Response({
            "loan_id": loan.id,
            "customer_id": customer_id,
            "loan_approved": approval,
            "message": message,
            "monthly_installment": monthly_installment,

        }, status=status.HTTP_201_CREATED)