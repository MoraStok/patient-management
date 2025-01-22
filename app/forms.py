from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    ReadOnlyPasswordHashField
    )
from django.forms import ValidationError

from .models import (
    CustomUser,
    ClinicalHistory,
    Patient,
    Staff,
    Calendar,
    CalendarEvent,
    Message
    )

class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'password1', 'password2']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name', 'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name', 'class': 'form-control'})
        self.fields['date_of_birth'].widget.attrs.update({'placeholder': 'Date of Birth', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email Address', 'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-control'})

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = 'doctor'
        if commit:
            user.save()
        return user

class StaffUserCreationForm(CustomUserCreationForm):
    class Meta:
        model = Staff
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'password1', 'password2', 'license']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['license'].widget.attrs.update({'placeholder': 'License', 'class': 'form-control'})
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = 'doctor'
        if commit:
            user.save()
        return user

class PatientUserCreationForm(CustomUserCreationForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'date_of_birth', 'email', 'password1', 'password2', 'social_sec_number']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['social_sec_number'].widget.attrs.update({'placeholder': 'Social Security Number', 'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = 'patient'
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ["email", "password", "date_of_birth", "first_name", "last_name", "is_active", "is_admin"]

class ClinicHistCreation(forms.ModelForm):
    model = ClinicalHistory
    fields = '__all__'

    prof = forms.ModelChoiceField(queryset=Staff.objects.all())
    patient = forms.ModelChoiceField(queryset=Patient.objects.all())

class CalendarCreation(forms.ModelForm):
    model = Calendar
    fields = '__all__'

    cal_events = forms.ModelChoiceField(queryset=CalendarEvent.objects.all())
    prof = forms.ModelChoiceField(queryset=Staff.objects.all())
    patient = forms.ModelChoiceField(queryset=Patient.objects.all())

# class AppointmentRequestForm(forms.ModelForm):
#     class Meta:
#         model = CalendarEvent
#         fields = ['patient', 'doctor', 'preferred_date', 'notes']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'content']  # Exclude recipient field
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter subject'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your message'}),
        }

    def __init__(self, *args, **kwargs):
        # Optionally, you can pass the sender as a keyword argument
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        message = super().save(commit=False)
        if self.sender:
            message.sender = self.sender  # Assign the sender
        if commit:
            message.save()
        return message