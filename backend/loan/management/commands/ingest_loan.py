from django.core.management.base import BaseCommand
from django.conf import settings
from customers.models import Customers
from loan.models import Loan
import openpyxl
import os
from datetime import datetime


class Command(BaseCommand):
    help = "Ingest loan data from Excel"

    def handle(self, *args, **kwargs):

        file_path = os.path.join(settings.BASE_DIR, "..", "data", "loan_data.xlsx")

        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active

        total = 0
        created = 0
        skipped = 0

        for row in sheet.iter_rows(min_row=2, values_only=True):
            total += 1

            try:
                customer_id = row[0]

                try:
                    customer = Customers.objects.get(id=customer_id)
                except Customers.DoesNotExist:
                    skipped += 1
                    continue

                Loan.objects.create(
                    customer=customer,
                    loan_amount=row[2],
                    tenure=int(row[3]),
                    interest_rate=row[4],
                    monthly_payment=row[5],
                    no_emi_paid_on_time=int(row[6]),
                    start_date=row[7] if isinstance(row[7], datetime) else None,
                    end_date=row[8] if isinstance(row[8], datetime) else None,
                )

                created += 1

            except Exception:
                skipped += 1

        print(f"Total rows: {total}")
        print(f"Created: {created}")
        print(f"Skipped: {skipped}")
