from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('staff/', views.StaffListView.as_view(), name='staff_list'),
    path('staff/add/', views.StaffCreateView.as_view(), name='add_staff'),
    path('staff/edit/<int:pk>/', views.StaffUpdateView.as_view(), name='edit_staff'),
    path('staff/delete/<int:pk>/', views.StaffDeleteView.as_view(), name='delete_staff'),
    path('staff/<int:pk>/history/', views.ServiceHistoryListView.as_view(), name='staff_history'),
    path('staff/<int:pk>/history/add/', views.ServiceHistoryCreateView.as_view(), name='add_history'),
    path('history/edit/<int:pk>/', views.ServiceHistoryUpdateView.as_view(), name='edit_history'),
    path('history/delete/<int:pk>/', views.ServiceHistoryDeleteView.as_view(), name='delete_history'),
    path('staff/<int:pk>/', views.StaffDetailView.as_view(), name='staff_detail'),
    path('staff/separate/<int:pk>/', views.StaffSeparateView.as_view(), name='separate_staff'),
    path('staff/terminated/', views.TerminatedStaffListView.as_view(), name='terminated_staff'),
    path('staff/restore/<int:pk>/', views.StaffRestoreView.as_view(), name='restore_staff'),
    path('staff/print/', views.StaffListPrintView.as_view(), name='staff_list_print'),
    path('staff/export/excel/', views.StaffExcelExportView.as_view(), name='export_excel'),
    path('staff/export/pdf/', views.StaffPdfExportView.as_view(), name='export_pdf'),
    path('staff/<int:pk>/disciplinary/', views.DisciplinaryActionListView.as_view(), name='disciplinary_list'),
    path('staff/<int:pk>/disciplinary/add/', views.DisciplinaryActionCreateView.as_view(), name='add_disciplinary'),
    path('disciplinary/edit/<int:pk>/', views.DisciplinaryActionUpdateView.as_view(), name='edit_disciplinary'),
    path('disciplinary/delete/<int:pk>/', views.DisciplinaryActionDeleteView.as_view(), name='delete_disciplinary'),
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard_stats'),
    path('backup/', views.BackupView.as_view(), name='backup_system'),
    path('restore/', views.RestoreView.as_view(), name='restore_system'),
    path('backup-restore/', views.BackupRestorePageView.as_view(), name='backup_restore'),
    path('change-password/', auth_views.PasswordChangeView.as_view(template_name='change_password.html', success_url='/accounts/password-changed/'), name='change_password'),
    path('password-changed/', auth_views.PasswordChangeDoneView.as_view(template_name='password_changed.html'), name='password_changed'),    
]