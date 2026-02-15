from customers.models import Customers
from .models import Loan
from django.db.models import Sum
from django.utils.timezone import now
from decimal import Decimal


def calculate_credit_score(customer_id, requested_amount):

    try:
        customer = Customers.objects.get(id=customer_id)
    except Customers.DoesNotExist:
        raise ValueError("Customer not found")

    loans = customer.loans.all()

    if not loans.exists():
        return 40

    score = 0

    approved_limit = customer.approved_limit or Decimal("0")

    today = now().date()
    active_loans = loans.filter(end_date__gte=today)

    total_active_amount = active_loans.aggregate(
        total=Sum("loan_amount")
    )["total"] or Decimal("0")

    if total_active_amount + Decimal(requested_amount) > approved_limit:
        return 0

    completed_loans = loans.filter(end_date__lt=today)

    if completed_loans.exists():
        total_ratio = 0
        for loan in completed_loans:
            if loan.tenure > 0:
                ratio = loan.no_emi_paid_on_time / loan.tenure
                total_ratio += ratio

        avg_ratio = total_ratio / completed_loans.count()

        score += avg_ratio * 40

    completed_count = completed_loans.count()

    if completed_count >= 5:
        score += 20
    elif completed_count >= 3:
        score += 15
    elif completed_count >= 1:
        score += 10

    current_year = today.year

    loans_this_year = loans.filter(start_date__year=current_year).count()

    if loans_this_year >= 3:
        score -= 10
    elif loans_this_year == 2:
        score -= 5

    total_loan_volume = loans.aggregate(
        total=Sum("loan_amount")
    )["total"] or Decimal("0")

    if approved_limit > 0:
        volume_ratio = total_loan_volume / approved_limit

        if volume_ratio >= 1:
            score += 20
        elif volume_ratio >= Decimal("0.5"):
            score += 10

    if score < 0:
        score = 0

    if score > 100:
        score = 100

    return int(score)



def correct_interest(credit_score, interest_rate):

    interest_rate = Decimal(interest_rate)

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
