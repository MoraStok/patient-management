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
    Professional,
    Calendar,
    CalendarEvent
    )

class CustomUserCreationForm(UserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

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
        # Adding placeholders and CSS classes for better styling
        self.fields['first_name'].widget.attrs.update({'placeholder': 'First Name', 'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Last Name', 'class': 'form-control'})
        self.fields['date_of_birth'].widget.attrs.update({'placeholder': 'Date of Birth', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Email Address', 'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-control'})

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
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

    prof = forms.ModelChoiceField(queryset=Professional.objects.all())
    patient = forms.ModelChoiceField(queryset=Patient.objects.all())

class CalendarCreation(forms.ModelForm):
    model = Calendar
    fields = '__all__'

    cal_events = forms.ModelChoiceField(queryset=CalendarEvent.objects.all())
    prof = forms.ModelChoiceField(queryset=Professional.objects.all())
    patient = forms.ModelChoiceField(queryset=Patient.objects.all())

# class AppointmentRequestForm(forms.ModelForm):
#     class Meta:
#         model = CalendarEvent
#         fields = ['patient', 'doctor', 'preferred_date', 'notes']


class MessageForm(forms.ModelForm):
    pass