from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_patient/', views.add_patient, name='add_patient'),
    path('view_patients/', views.view_patient, name='view_patients'),
    path('manage_appointments/', views.manage_appointments, name='manage_appointments'),
    path('request_appointment/', views.request_appointment, name='request_appointment'),
    path('view_medications/', views.view_medications, name='view_medications'),
    path('send_message/', views.send_message, name='send_message'),
]