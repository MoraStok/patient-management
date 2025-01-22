from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required

from .forms import PatientUserCreationForm, MessageForm, StaffUserCreationForm
from .models import Patient

def patient_signup(request):
    if request.method == 'POST':
        form = PatientUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('login'))
    else:
        form = PatientUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def staff_signup(request):
    if request.method == 'POST':
        form = StaffUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('login'))
    else:
        form = StaffUserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def dashboard(request):
    # Get the user's role
    user_role = request.user.role  # or use request.user.groups if you're using groups
    
    if user_role == 'doctor' or user_role == 'assistant':
        return render(request, 'doctor_assist/doctor_assistant_dashboard.html')
    elif user_role == 'patient':
        return render(request, 'patient/patient_dashboard.html')
    else:
        # Default to patient view if no role is set
        return render(request, 'home.html')

## PATIENT VIEWS ##
@login_required
def send_message(request):
    try:
        # Ensure the logged-in user is a Patient
        patient = Patient.objects.filter(customuser_ptr=request.user).first()
        print(patient)
    except Patient.DoesNotExist:
        return render(request, 'error.html', {'error': 'You are not registered as a patient.'})
    else:
        if not patient.prof_in_charge:
            return render(request, 'error.html', {'error': 'No doctor is assigned to you.'})
        
        # Retrieve the doctor assigned to the patient
        doctor = patient.prof_in_charge

        if request.method == 'POST':
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.sender = request.user  # Set the sender to the logged-in patient
                message.recipient = doctor.user  # Set the recipient to the doctor's user account
                message.save()
                return redirect('dashboard')  # Redirect to a success page
        else:
            form = MessageForm()

        return render(request, 'patient/send_message.html', {'form': form})

@login_required
def add_patient(request):
    form = MessageForm(request.POST)
    return render(request, 'patient/add_patient.html', {'form': form})

@login_required
def view_patient(request):
    form = MessageForm(request.POST)
    return render(request, 'patient/view_patient.html', {'form': form})

@login_required
def request_appointment(request):
    form = MessageForm(request.POST)
    return render(request, 'patient/request_appointment.html', {'form': form})

@login_required
def view_medications(request):
    form = MessageForm(request.POST)
    return render(request, 'patient/view_medications.html', {'form': form})


## DOCTOR/ASSISTANT VIEWS ##
@login_required
def manage_appointments(request):
    form = MessageForm(request.POST)
    return render(request, 'doctor_assist/manage_appointments.html', {'form': form})
