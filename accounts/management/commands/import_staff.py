import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from accounts.models import StaffMember


class Command(BaseCommand):
    help = 'Delete existing staff and import staff records from staff.xls'

    def handle(self, *args, **kwargs):

        # Read Excel file
        df = pd.read_excel(
            'staff.xls',
            sheet_name='For MOR',
            header=0
        )

        contract_map = {
            'Direct Employee': 'pay_scale',
            'Pay Scale': 'pay_scale',
            'Short Contract': 'short_contract',
            'Railway Employee': 'railway_employee',
            'Other': 'other',
        }

        gender_map = {
            'Male': 'male',
            'Female': 'female',
        }

        # Delete existing staff records
        deleted_count, _ = StaffMember.objects.all().delete()

        self.stdout.write(
            self.style.WARNING(
                f'{deleted_count} existing staff records deleted.'
            )
        )

        created_count = 0
        skipped_count = 0

        # Import records from Excel
        for index, row in df.iterrows():

            try:
                # Convert date from dd-mm-yyyy text to Python date
                date_str = str(row['date_of_joining']).strip()
                date_str = date_str.replace('.', '-')

                date_obj = datetime.strptime(
                    date_str,
                    '%d-%m-%Y'
                ).date()

                # Basic pay
                if pd.isna(row['basic_pay']):
                    basic_pay = 0
                else:
                    basic_pay = float(row['basic_pay'])

                # Gross pay
                if pd.isna(row['gross_pay']):
                    gross_pay = 0
                else:
                    gross_pay = float(row['gross_pay'])

                # Gender
                if pd.isna(row['gender']):
                    gender = 'male'
                else:
                    gender = gender_map.get(
                        str(row['gender']).strip(),
                        'male'
                    )

                # Contract type
                contract_type = contract_map.get(
                    str(row['contract_type']).strip(),
                    'other'
                )

                StaffMember.objects.create(
                    serial_number=int(row['serial_number']),
                    name=str(row['name']).strip(),
                    designation=str(row['designation']).strip(),
                    pay_scale=str(row['pay_scale']).strip(),
                    date_of_joining=date_obj,
                    basic_pay=basic_pay,
                    posting_place=str(row['posting_place']).strip(),
                    gross_pay=gross_pay,
                    contract_type=contract_type,
                    gender=gender,
                )

                created_count += 1

            except Exception as e:

                skipped_count += 1

                self.stdout.write(
                    self.style.WARNING(
                        f"Row {index + 2} skipped: {e}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Import finished: {created_count} created, "
                f"{skipped_count} skipped."
            )
        )