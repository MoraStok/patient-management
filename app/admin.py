from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import CustomUserChangeForm, CustomUserCreationForm, ClinicHistCreation

from .models import (
    CustomUser,
    ClinicalHistory,
    Calendar,
    Professional,
    Patient
)

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["email", "date_of_birth", "first_name", "last_name", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["date_of_birth", "first_name", "last_name"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "date_of_birth", "first_name", "last_name", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []

# Now register the new UserAdmin...
admin.site.register(CustomUser, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'prof')

@admin.register(ClinicalHistory)
class ClinicAdmin(admin.ModelAdmin):
    form = ClinicHistCreation
    list_display = ('id',)
    raw_id_fields = ('prof', 'patient')

@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name','last_name', 'is_active')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name','social_sec_number', 'is_active')
    list_filter = ('prof_in_charge', 'is_active')
