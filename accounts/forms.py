from django import forms
from .models import StaffMember

'''class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = ['serial_number', 'name', 'designation', 'pay_scale', 'date_of_joining',
                  'basic_pay', 'posting_place', 'gross_pay', 'gender']
'''
class StaffMemberForm(forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = ['serial_number', 'name', 'designation', 'pay_scale', 'date_of_joining',
                  'basic_pay', 'posting_place', 'gross_pay', 'photo', 'contract_type', 'status', 'separation_date']        

class DisciplinaryActionForm(forms.ModelForm):
    class Meta:
        model = DisciplinaryAction
        fields = ['date', 'action_type', 'description']        