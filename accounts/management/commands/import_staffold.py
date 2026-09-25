import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from accounts.models import StaffMember


class Command(BaseCommand):
    help = 'Import staff records from staff.xls'

    def handle(self, *args, **kwargs):
        df = pd.read_excel('staff.xls', sheet_name='For MOR', header=0)

        contract_map = {
    'Direct Employee': 'pay_scale',
    'Pay Scale': 'pay_scale',
    'Short Contract': 'short_contract',
}
        gender_map = {
            'Male': 'male',
            'Female': 'female',
        }

        created_count = 0
        skipped_count = 0

        for index, row in df.iterrows():
            try:
                date_str = str(row['date_of_joining']).strip().replace('.', '-')
                date_obj = datetime.strptime(date_str, '%d-%m-%Y').date()

                StaffMember.objects.create(
                    serial_number=row['serial_number'],
                    name=row['name'],
                    designation=row['designation'],
                    pay_scale=str(row['pay_scale']),
                    date_of_joining=date_obj,
                    basic_pay=0,
                    posting_place=row['posting_place'],
                    gross_pay=row['gross_pay'],
                    contract_type=contract_map.get(row['contract_type'], 'other'),
                    gender=gender_map.get(row['gender'], 'male'),
                )
                created_count += 1
            except Exception as e:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"Row {index + 2} skipped: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Import finished: {created_count} created, {skipped_count} skipped."))