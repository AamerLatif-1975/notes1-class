# Register your models here.
from django.contrib import admin
from .models import StaffMember, ServiceHistory, AuditLog

admin.site.register(StaffMember)
admin.site.register(ServiceHistory)
admin.site.register(AuditLog)
