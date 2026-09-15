# Register your models here.
from django.contrib import admin
from .models import StaffMember, ServiceHistory

admin.site.register(StaffMember)
admin.site.register(ServiceHistory)
