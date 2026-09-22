# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.utils import timezone

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View

from .models import StaffMember, ServiceHistory, DisciplinaryAction, AuditLog

import openpyxl
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO


# ---------------------------------------------------------------------------
# Auth: signup (staff/admin only) and home
# ---------------------------------------------------------------------------

@login_required
@user_passes_test(lambda u: u.is_staff)
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff_list')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_required
def home(request):
    return render(request, 'home.html')


# ---------------------------------------------------------------------------
# StaffMember: list, terminated list, detail
# ---------------------------------------------------------------------------

class StaffListView(LoginRequiredMixin, ListView):
    model = StaffMember
    template_name = 'staff_list.html'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        status = self.request.GET.get('status')
        gender = self.request.GET.get('gender')
        contract_type = self.request.GET.get('contract_type')
        posting_place = self.request.GET.get('posting_place')
        queryset = StaffMember.objects.all()

        if query:
            queryset = queryset.filter(name__icontains=query)

        if status:
            queryset = queryset.filter(status=status)

        if gender:
            queryset = queryset.filter(gender=gender)

        if contract_type:
            queryset = queryset.filter(contract_type=contract_type)
        if posting_place:
            queryset = queryset.filter(posting_place=posting_place)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['posting_places'] = (
            StaffMember.objects
            .values_list('posting_place', flat=True)
            .distinct()
            .order_by('posting_place')
        )

        return context

class TerminatedStaffListView(LoginRequiredMixin, ListView):
    model = StaffMember
    template_name = 'terminated_staff_list.html'
    paginate_by = 10

    def get_queryset(self):
        return StaffMember.objects.exclude(status='active')


class StaffDetailView(LoginRequiredMixin, DetailView):
    model = StaffMember
    template_name = 'staff_detail.html'


# ---------------------------------------------------------------------------
# StaffMember: create, update, delete
# ---------------------------------------------------------------------------

STAFF_FIELDS = [
    'serial_number',
    'name',
    'designation',
    'pay_scale',
    'date_of_joining',
    'basic_pay',
    'posting_place',
    'gross_pay',
    'photo',
    'contract_type',
    'gender',
    'status',
    'separation_date',
]


class StaffCreateView(LoginRequiredMixin, CreateView):
    model = StaffMember
    fields = STAFF_FIELDS
    template_name = 'add_staff.html'
    success_url = '/accounts/staff/'

    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLog.objects.create(
            user=self.request.user,
            action='created',
            model_name='StaffMember',
            object_repr=str(self.object),
        )
        return response


class StaffUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StaffMember
    fields = STAFF_FIELDS
    template_name = 'add_staff.html'
    success_url = '/accounts/staff/'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLog.objects.create(
            user=self.request.user,
            action='updated',
            model_name='StaffMember',
            object_repr=str(self.object),
        )
        return response


class StaffDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = StaffMember
    template_name = 'confirm_delete_staff.html'
    success_url = '/accounts/staff/'

    def test_func(self):
        return self.request.user.is_superuser

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        AuditLog.objects.create(
            user=request.user,
            action='deleted',
            model_name='StaffMember',
            object_repr=str(self.object),
        )
        return super().delete(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# StaffMember: separate (soft-delete) and restore
# ---------------------------------------------------------------------------

class StaffSeparateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StaffMember
    fields = ['status', 'separation_date']
    template_name = 'staff_separate.html'
    success_url = '/accounts/staff/'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        if not form.instance.separation_date:
            form.instance.separation_date = timezone.now().date()

        result = super().form_valid(form)
        ServiceHistory.objects.create(
            staff=self.object,
            position=f"Not in Service ({self.object.get_status_display()})",
            start_date=self.object.separation_date,
            end_date=None,
            salary=0,
            performance_rating='',
        )
        AuditLog.objects.create(
            user=self.request.user,
            action='separated',
            model_name='StaffMember',
            object_repr=str(self.object),
        )
        return result


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

        gap_record = ServiceHistory.objects.filter(
            staff=self.object,
            position__icontains='Not in Service',
            end_date__isnull=True
        ).first()

        if gap_record:
            gap_record.end_date = timezone.now().date()
            gap_record.save()

        AuditLog.objects.create(
            user=self.request.user,
            action='restored',
            model_name='StaffMember',
            object_repr=str(self.object),
        )
        return redirect(self.success_url)


# ---------------------------------------------------------------------------
# ServiceHistory: list, create, update, delete (scoped to one staff member)
# ---------------------------------------------------------------------------

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


class ServiceHistoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ServiceHistory
    template_name = 'confirm_delete_history.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return f'/accounts/staff/{self.object.staff.pk}/history/'


# ---------------------------------------------------------------------------
# DisciplinaryAction: list, create, update, delete (scoped to one staff member)
# ---------------------------------------------------------------------------

class DisciplinaryActionListView(LoginRequiredMixin, ListView):
    model = DisciplinaryAction
    template_name = 'disciplinary_list.html'

    def get_queryset(self):
        self.staff = get_object_or_404(StaffMember, pk=self.kwargs['pk'])
        return DisciplinaryAction.objects.filter(staff=self.staff)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff'] = self.staff
        return context


class DisciplinaryActionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = DisciplinaryAction
    fields = ['date', 'action_type', 'description']
    template_name = 'add_disciplinary.html'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        self.staff = get_object_or_404(StaffMember, pk=self.kwargs['pk'])
        form.instance.staff = self.staff
        response = super().form_valid(form)
        AuditLog.objects.create(
            user=self.request.user,
            action='created',
            model_name='DisciplinaryAction',
            object_repr=str(self.object),
        )
        return response

    def get_success_url(self):
        return f'/accounts/staff/{self.staff.pk}/disciplinary/'


class DisciplinaryActionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = DisciplinaryAction
    fields = ['date', 'action_type', 'description']
    template_name = 'add_disciplinary.html'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLog.objects.create(
            user=self.request.user,
            action='updated',
            model_name='DisciplinaryAction',
            object_repr=str(self.object),
        )
        return response

    def get_success_url(self):
        return f'/accounts/staff/{self.object.staff.pk}/disciplinary/'


class DisciplinaryActionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = DisciplinaryAction
    template_name = 'confirm_delete_disciplinary.html'

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        AuditLog.objects.create(
            user=request.user,
            action='deleted',
            model_name='DisciplinaryAction',
            object_repr=str(self.object),
        )
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return f'/accounts/staff/{self.object.staff.pk}/disciplinary/'


# ---------------------------------------------------------------------------
# Reports: print view, Excel export, PDF export
# ---------------------------------------------------------------------------

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

'''
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

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="staff_list.xlsx"'
        wb.save(response)
        return response
'''
class StaffExcelExportView(LoginRequiredMixin, View):
    def get(self, request):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Staff List"

        ws.append([
            'S#',
            'Name',
            'Designation',
            'Pay Scale',
            'Date of Joining',
            'Posting Place',
            'Status'
        ])

        # Get filters from the URL
        query = request.GET.get('q')
        status = request.GET.get('status')
        gender = request.GET.get('gender')
        contract_type = request.GET.get('contract_type')

        # Start with all staff
        staff = StaffMember.objects.all()

        # Apply filters
        if query:
            staff = staff.filter(name__icontains=query)

        if status:
            staff = staff.filter(status=status)

        if gender:
            staff = staff.filter(gender=gender)

        if contract_type:
            staff = staff.filter(contract_type=contract_type)

        # Add filtered staff to Excel
        for i, member in enumerate(staff, start=1):
            ws.append([
                i,
                member.name,
                member.designation,
                member.pay_scale,
                member.date_of_joining.strftime('%d-%m-%Y'),
                member.posting_place,
                member.get_status_display()
            ])

        # Format header
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Create borders
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Apply borders and alignment to all cells
        for row in ws.iter_rows():
            for cell in row:
                cell.border = thin_border
                cell.alignment = Alignment(
                    horizontal='center',
                    vertical='center',
                    wrap_text=True
                )

        # Adjust column widths
        column_widths = {
            'A': 8,
            'B': 25,
            'C': 25,
            'D': 12,
            'E': 18,
            'F': 25,
            'G': 15,
        }

        for column, width in column_widths.items():
            ws.column_dimensions[column].width = width

        # Adjust row heights
        ws.row_dimensions[1].height = 25

        for row in range(2, ws.max_row + 1):
            ws.row_dimensions[row].height = 22
        
        ws.freeze_panes = 'A2'
      

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        response['Content-Disposition'] = 'attachment; filename="staff_list.xlsx"'

        wb.save(response)

        return response


class StaffPdfExportView(LoginRequiredMixin, View):
    def get(self, request):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()

        elements = [Paragraph("Staff List Report", styles['Title'])]

        data = [[
            'S#',
            'Name',
            'Designation',
            'Pay Scale',
            'Date of Joining',
            'Posting Place'
        ]]

        # Get filters from the URL
        query = request.GET.get('q')
        status = request.GET.get('status')
        gender = request.GET.get('gender')
        contract_type = request.GET.get('contract_type')

        # Start with all staff
        staff = StaffMember.objects.all()

        # Apply filters
        if query:
            staff = staff.filter(name__icontains=query)

        if status:
            staff = staff.filter(status=status)

        if gender:
            staff = staff.filter(gender=gender)

        if contract_type:
            staff = staff.filter(contract_type=contract_type)

        # Add filtered staff to PDF
        for i, member in enumerate(staff, start=1):
            data.append([
                i,
                member.name,
                member.designation,
                member.pay_scale,
                member.date_of_joining.strftime('%d-%m-%Y'),
                member.posting_place
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

        response = HttpResponse(
            buffer,
            content_type='application/pdf'
        )

        response['Content-Disposition'] = 'attachment; filename="staff_list.pdf"'

        return response



from django.db.models import Count

class DashboardStatsView(LoginRequiredMixin, View):
    def get(self, request):
        active_staff = StaffMember.objects.filter(status='active')

        context = {
            'total_active': active_staff.count(),
            'total_terminated': StaffMember.objects.exclude(status='active').count(),
            'by_gender': active_staff.values('gender').annotate(count=Count('id')),
            'by_contract': active_staff.values('contract_type').annotate(count=Count('id')),
            'recent_separations': StaffMember.objects.exclude(status='active').order_by('-separation_date')[:5],
        }
        return render(request, 'dashboard_stats.html', context)