
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


class ViewLoanbyId(APIView):

    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(id=loan_id)
        except Loan.DoesNotExist:
            return Response(
                {"error": "Loan not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        customer = loan.customer

        return Response(
            {
                "loan_id": loan.id,
                "customer": {
                    "id": customer.id,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "phone_number": customer.phone_number,
                    "age": customer.age,
                },
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_payment,
                "tenure": loan.tenure,
            },
            status=status.HTTP_200_OK,
        )

class ViewLoansByCustomer(APIView):

    def get(self, request, customer_id):
        try:
            customer = Customers.objects.get(id=customer_id)
        except Customers.DoesNotExist:
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        today = now().date()

        active_loans = customer.loans.filter(end_date__gte=today)

        response_data = []

        for loan in active_loans:
            months_passed = (
                (today.year - loan.start_date.year) * 12
                + (today.month - loan.start_date.month)
            )

            repayments_left = loan.tenure - months_passed
            if repayments_left < 0:
                repayments_left = 0

            response_data.append({
                "loan_id": loan.id,
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_payment,
                "repayments_left": repayments_left,
            })

        return Response(response_data, status=status.HTTP_200_OK)
