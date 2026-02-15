from django.core.management.base import BaseCommand
from django.conf import settings
from customers.models import Customers
import openpyxl
import os

class Command(BaseCommand):
    help = "Ingest customer data from Excel"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, "..", "data", "customer_data.xlsx")

        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active

        total = 0
        created = 0
        skipped = 0

        for row in sheet.iter_rows(min_row=2, values_only=True):
            total += 1
            try:
                if Customers.objects.filter(phone_number=str(row[4])).exists():
                    skipped += 1
                    continue

                Customers.objects.create(
                    first_name=str(row[1]),
                    last_name=str(row[2]),
                    age=int(row[3]) if row[3] else None,
                    phone_number=str(row[4]),
                    monthly_salary=row[5],
                    approved_limit=row[6],
                )

                created += 1

            except Exception:
                skipped += 1

        print(f"Total rows: {total}")
        print(f"Created: {created}")
        print(f"Skipped: {skipped}")
