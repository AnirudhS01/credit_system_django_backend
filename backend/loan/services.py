from customers.models import Customers
from .models import Loan
from django.db.models import Sum
from django.utils.timezone import now
from decimal import Decimal


def calculate_credit_score(customer_id, requested_amount):
    """
    Calculate the credit score based on the customer's history and the requested amount.
    - works for existing and new customers
    returns credit score
    """

    try:
        #lets check if customer exists
        customer = Customers.objects.get(id=customer_id)
    except Customers.DoesNotExist:
        #if not raise run time value error
        raise ValueError("Customer not found")

    loans = customer.loans.all()
    #check if any loan for the customer id exists
    if not loans.exists():
        #if not loan then return a nuetral credit score of 40
        return 40

    score = 0

    approved_limit = customer.approved_limit or Decimal("0")

    today = now().date()
    #fetch all active loans
    active_loans = loans.filter(end_date__gte=today)
    #fetch if sum of all active loans is greater than approved limit
    total_active_amount = active_loans.aggregate(
        total=Sum("loan_amount")
    )["total"] or Decimal("0")
    # return 0 if sum is greater as mentioned in the docs
    if total_active_amount + Decimal(requested_amount) > approved_limit:
        return 0

    completed_loans = loans.filter(end_date__lt=today)
    #fetch all completed loans and see if they are paid on time 
    # can be calculated by no_emi_paid_on_time / tenure
    if completed_loans.exists():
        total_ratio = 0
        for loan in completed_loans:
            if loan.tenure > 0:
                ratio = loan.no_emi_paid_on_time / loan.tenure
                total_ratio += ratio

        avg_ratio = total_ratio / completed_loans.count()

        score += avg_ratio * 40

    completed_count = completed_loans.count()
    # assigning points based on the completed loans
    if completed_count >= 5:
        score += 20
    elif completed_count >= 3:
        score += 15
    elif completed_count >= 1:
        score += 10

    current_year = today.year

    loans_this_year = loans.filter(start_date__year=current_year).count()
    #assigning points based on the loans taken in the current year
    if loans_this_year >= 3:
        score -= 10
    elif loans_this_year == 2:
        score -= 5

    total_loan_volume = loans.aggregate(
        total=Sum("loan_amount")
    )["total"] or Decimal("0")
    #assigning points based on the total loan volume
    if approved_limit > 0:
        volume_ratio = total_loan_volume / approved_limit

        if volume_ratio >= 1:
            score += 20
        elif volume_ratio >= Decimal("0.5"):
            score += 10
    # just to make sure they dont go out of bounds
    if score < 0:
        score = 0

    if score > 100:
        score = 100

    return int(score)



def correct_interest(credit_score, interest_rate):
    """
    Correct the interest rate based on the credit score.
    - this is purely based on the docs
    - returns interest rate ( corrected )
    """

    interest_rate = Decimal(interest_rate)
    #baed on docs
    if credit_score > 50:
        min_rate = Decimal("0")
    elif 30 < credit_score <= 50:
        min_rate = Decimal("12")
    elif 10 < credit_score <= 30:
        min_rate = Decimal("16")
    else:
        return None

    if interest_rate < min_rate:
        return min_rate

    return interest_rate

from decimal import Decimal, getcontext

getcontext().prec = 28


def calculate_emi(loan_amount, interest_rate, tenure):
    """
    Calculate the EMI based on the loan amount, interest rate, and tenure.
    - math formula , compound interest
    - returns the emi / montly amount to be paid
    """

    P = Decimal(loan_amount)
    annual_rate = Decimal(interest_rate)

    if tenure <= 0:
        return Decimal("0")

    monthly_rate = annual_rate / Decimal("100") / Decimal("12")

    if monthly_rate == 0:
        return P / Decimal(tenure)

    one_plus_r_pow_n = (Decimal("1") + monthly_rate) ** tenure

    emi = (
        P * monthly_rate * one_plus_r_pow_n
    ) / (one_plus_r_pow_n - Decimal("1"))

    return emi.quantize(Decimal("0.01"))

def eligibility(customer_id , loan_amount,tenure , interest_rate):
    """
    Check if the person is eligible for the loan
    - calls the credit , interest , emi functions
    - returns approval status , also decided to include a message 
    """
    try:
        customer = Customers.objects.get(id=customer_id)
    except Customers.DoesNotExist:
        raise ValueError("Customer not found")
    # call credit , correct_interest , emi functions 
    credit_score = calculate_credit_score(customer_id , loan_amount)
    if credit_score == 0:
        return False , None , None, "Exceeded approved limit"
    corrected_interest = correct_interest(credit_score , interest_rate)
    #if credit score was too low it would have returned None
    #so return false , montlhy installment and corrected interest rate all togther  
    if corrected_interest is None:
        return False , None , None, "Credit score too low"
    else:
        monthly_installment = calculate_emi( loan_amount,corrected_interest,tenure)

        current_emi_total = customer.loans.filter(
            end_date__gte=now().date()
        ).aggregate(total=Sum("monthly_payment"))["total"] or Decimal("0")
        #check if monthly installment sum is greater than 50% of monthly salary
        if current_emi_total + monthly_installment > (customer.monthly_salary * Decimal("0.5")):
            return False , monthly_installment , corrected_interest, "Monthly installment greater than 50% of salary"
        else:
            return True , monthly_installment , corrected_interest, "Approved"

    

    
