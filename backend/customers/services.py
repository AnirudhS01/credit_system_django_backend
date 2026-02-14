def calculate_limit(monthly_salary):
    sal = 36*monthly_salary
    #rounded to the nearest lakh
    # lets divide by 1l and then round the number and mul by 1l
    val = sal/100000
    val = round(val)
    val = val*100000
    return val

