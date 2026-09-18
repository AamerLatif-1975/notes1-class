from django.shortcuts import render

# Create your views here.
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.views.generic.edit import CreateView
from .models import StaffMember, ServiceHistory
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.views.generic.edit import UpdateView
from django.utils import timezone
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    return render(request, 'home.html')

class StaffListView(LoginRequiredMixin, ListView):
    model = StaffMember
    template_name = 'staff_list.html'
    paginate_by = 10
    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = StaffMember.objects.filter(status='active')
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset
    

class TerminatedStaffListView(LoginRequiredMixin, ListView):
    model = StaffMember
    template_name = 'terminated_staff_list.html'
    paginate_by = 10

    def get_queryset(self):
        return StaffMember.objects.exclude(status='active')  
     
class StaffCreateView(LoginRequiredMixin, CreateView):  
#class StaffCreateView(CreateView):
    model = StaffMember
    fields = ['serial_number', 'name', 'designation', 'pay_scale', 'date_of_joining',
              'basic_pay', 'posting_place', 'gross_pay', 'photo', 'contract_type', 'gender', 'status', 'separation_date']
    template_name = 'add_staff.html'
    success_url = '/accounts/staff/'

class StaffUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StaffMember
    fields = ['serial_number', 'name', 'designation', 'pay_scale', 'date_of_joining', 'basic_pay', 'posting_place', 'gross_pay', 'photo', 'contract_type', 'gender', 'status', 'separation_date']
    template_name = 'add_staff.html'
    success_url = '/accounts/staff/'

    def test_func(self):
        return self.request.user.is_staff
'''class StaffUpdateView(UpdateView):
    model = StaffMember
    fields = ['serial_number', 'name', 'designation', 'pay_scale', 'date_of_joining', 'basic_pay', 'posting_place', 'gross_pay']
    template_name = 'add_staff.html'
    success_url = '/accounts/staff/'  
class StaffDeleteView(DeleteView):
    model = StaffMember
    template_name = 'confirm_delete_staff.html'
    success_url = '/accounts/staff/' ''' 

class StaffDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = StaffMember
    template_name = 'confirm_delete_staff.html'
    success_url = '/accounts/staff/'

    def test_func(self):
        return self.request.user.is_superuser  


class StaffSeparateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StaffMember
    fields = ['status', 'separation_date']
    template_name = 'staff_separate.html'
    success_url = '/accounts/staff/'

    def test_func(self):
        return self.request.user.is_staff
        #return self.request.user.is_authenticated

    def form_valid(self, response):
        result = super().form_valid(response)
        ServiceHistory.objects.create(
            staff=self.object,
            position=f"Not in Service ({self.object.get_status_display()})",
            start_date=self.object.separation_date,
            end_date=None,
            salary=0,
            performance_rating='',
        )
        return result
'''class StaffSeparateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StaffMember
    fields = ['status', 'separation_date']
    template_name = 'staff_separate.html'
    success_url = '/accounts/staff/'

    def test_func(self):
        return self.request.user.is_authenticated '''
  #  def test_func(self):
   #     return self.request.user.is_staff

class StaffRestoreView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StaffMember
    fields = []
    template_name = 'staff_restore.html'
    success_url = '/accounts/staff/'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        self.object.status = 'active'
        self.object.save()

        open_gap = ServiceHistory.objects.filter(
            staff=self.object, end_date__isnull=True
        ).exclude(position__icontains='Not in Service').first()
        # (see note below about this line)

        gap_record = ServiceHistory.objects.filter(
            staff=self.object,
            position__icontains='Not in Service',
            end_date__isnull=True
        ).first()
        if gap_record:
            gap_record.end_date = timezone.now().date()
            gap_record.save()

        return redirect(self.success_url)   

class ServiceHistoryListView(LoginRequiredMixin, ListView):
    model = ServiceHistory
    template_name = 'staff_history.html'

    def get_queryset(self):
        self.staff = get_object_or_404(StaffMember, pk=self.kwargs['pk'])
        return ServiceHistory.objects.filter(staff=self.staff)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff'] = self.staff
        return context    

class ServiceHistoryCreateView(LoginRequiredMixin, CreateView):
    model = ServiceHistory
    fields = ['position', 'start_date', 'end_date', 'salary', 'performance_rating']
    template_name = 'add_history.html'

    def form_valid(self, form):
        self.staff = get_object_or_404(StaffMember, pk=self.kwargs['pk'])
        form.instance.staff = self.staff
        return super().form_valid(form)

    def get_success_url(self):
        return f'/accounts/staff/{self.staff.pk}/history/'    

class ServiceHistoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ServiceHistory
    fields = ['position', 'start_date', 'end_date', 'salary', 'performance_rating']
    template_name = 'add_history.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return f'/accounts/staff/{self.object.staff.pk}/history/'
'''class ServiceHistoryUpdateView(UpdateView):
    model = ServiceHistory
    fields = ['position', 'start_date', 'end_date', 'salary', 'performance_rating']
    template_name = 'add_history.html'

    def get_success_url(self):
        return f'/accounts/staff/{self.object.staff.pk}/history/'

class ServiceHistoryDeleteView(DeleteView):
    model = ServiceHistory
    template_name = 'confirm_delete_history.html'

    def get_success_url(self):
        return f'/accounts/staff/{self.object.staff.pk}/history/' '''
class ServiceHistoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ServiceHistory
    template_name = 'confirm_delete_history.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return f'/accounts/staff/{self.object.staff.pk}/history/'

from django.views.generic import DetailView
class StaffDetailView(LoginRequiredMixin, DetailView):
#class StaffDetailView(DetailView):
    model = StaffMember
    template_name = 'staff_detail.html'    
from django.utils import timezone

class StaffListPrintView(LoginRequiredMixin, ListView):
    model = StaffMember
    template_name = 'staff_list_print.html'
    context_object_name = 'staff'

    def get_queryset(self):
        return StaffMember.objects.filter(status='active')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_date'] = timezone.now().strftime('%d %B %Y')
        return context
import openpyxl
from django.http import HttpResponse

class StaffExcelExportView(LoginRequiredMixin, View):
    def get(self, request):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Staff List"

        ws.append(['S#', 'Name', 'Designation', 'Pay Scale', 'Date of Joining', 'Posting Place', 'Status'])

        staff = StaffMember.objects.filter(status='active')
        for i, member in enumerate(staff, start=1):
            ws.append([
                i, member.name, member.designation, member.pay_scale,
                member.date_of_joining.strftime('%d-%m-%Y'),
                member.posting_place, member.get_status_display()
            ])

        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="staff_list.xlsx"'
        wb.save(response)
        return response   

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO

class StaffPdfExportView(LoginRequiredMixin, View):
    def get(self, request):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        elements = [Paragraph("Staff List Report", styles['Title'])]

        data = [['S#', 'Name', 'Designation', 'Pay Scale', 'Date of Joining', 'Posting Place']]
        staff = StaffMember.objects.filter(status='active')
        for i, member in enumerate(staff, start=1):
            data.append([
                i, member.name, member.designation, member.pay_scale,
                member.date_of_joining.strftime('%d-%m-%Y'), member.posting_place
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a3c6e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(table)

        doc.build(elements)
        buffer.seek(0)

        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="staff_list.pdf"'
        return response     