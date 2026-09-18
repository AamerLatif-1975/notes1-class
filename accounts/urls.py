from django.urls import path
from . import views

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
]