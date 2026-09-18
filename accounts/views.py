from django.shortcuts import render

# Create your views here.
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from .models import StaffMember, ServiceHistory
from django.shortcuts import get_object_or_404
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

class StaffListView(ListView):
    model = StaffMember
    template_name = 'staff_list.html'
    paginate_by = 2
    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return StaffMember.objects.filter(name__icontains=query)
        return StaffMember.objects.all()

class StaffCreateView(CreateView):
    model = StaffMember
    fields = ['serial_number', 'name', 'designation', 'pay_scale', 'date_of_joining',
              'basic_pay', 'posting_place', 'gross_pay', 'photo', 'contract_type', 'gender']
    template_name = 'add_staff.html'
    success_url = '/accounts/staff/'

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class StaffUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = StaffMember
    fields = ['serial_number', 'name', 'designation', 'pay_scale', 'date_of_joining', 'basic_pay', 'posting_place', 'gross_pay', 'photo', 'contract_type', 'gender']
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
        return self.request.user.is_staff    

class ServiceHistoryListView(ListView):
    model = ServiceHistory
    template_name = 'staff_history.html'

    def get_queryset(self):
        self.staff = get_object_or_404(StaffMember, pk=self.kwargs['pk'])
        return ServiceHistory.objects.filter(staff=self.staff)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['staff'] = self.staff
        return context    

class ServiceHistoryCreateView(CreateView):
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

class StaffDetailView(DetailView):
    model = StaffMember
    template_name = 'staff_detail.html'    