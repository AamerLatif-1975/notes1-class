# Create your models here.
from django.db import models
class StaffMember(models.Model):
    CONTRACT_TYPE_CHOICES = [
        ('short_contract', 'Short Contract'),
        ('pay_scale', 'Pay Scale'),
        ('railway_employee', 'Railway Employee'),
        ('other', 'Other'),
    ]

    serial_number = models.IntegerField()
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    pay_scale = models.CharField(max_length=20)
    date_of_joining = models.DateField()
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2)
    posting_place = models.CharField(max_length=100)
    gross_pay = models.DecimalField(max_digits=10, decimal_places=2)
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPE_CHOICES)

    class Meta:
        ordering = ['serial_number']

    def __str__(self):
        return self.name

class ServiceHistory(models.Model):
    staff = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='history')
    position = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    performance_rating = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.staff.name} - {self.position}"    