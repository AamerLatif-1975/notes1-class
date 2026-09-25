# Create your models here.
from django.db import models
class StaffMember(models.Model):
    CONTRACT_TYPE_CHOICES = [
        ('short_contract', 'Short Contract'),
        ('pay_scale', 'Pay Scale'),
        ('railway_employee', 'Railway Employee'),
        ('other', 'Other'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    STATUS_CHOICES = [
    ('active', 'Active'),
    ('resigned', 'Resigned'),
    ('terminated', 'Terminated'),
    ('repatriated', 'Repatriated'),
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
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    #gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    separation_date = models.DateField(blank=True, null=True)
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

class DisciplinaryAction(models.Model):
    ACTION_TYPE_CHOICES = [
        ('warning', 'Warning'),
        ('show_cause', 'Show Cause Notice'),
        ('penalty', 'Penalty'),
        ('suspension', 'Suspension'),
        ('other', 'Other'),
    ]

    staff = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='disciplinary_actions')
    date = models.DateField()
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.staff.name} - {self.get_action_type_display()}"  

from django.contrib.auth.models import User
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('separated', 'Separated'),
        ('restored', 'Restored'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_repr = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name}: {self.object_repr}"
      