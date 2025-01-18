from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError

## CUSTOM USER MODEL ##
class UserManager(BaseUserManager):
    def create_user(self, email, date_of_birth, first_name, last_name, password=None, role='patient'):
        """
        Creates and saves a User with the given email, date of
        birth, name and password. 
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, first_name, last_name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth, name and password.
        """
        user = self.create_user(
            email,
            password=password,
            date_of_birth=date_of_birth,
            first_name=first_name,
            last_name=last_name,
            role='doctor',
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('assistant', 'Doctor\'s Assistant'),
        ('patient', 'Patient'),
    ]
    username = None
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    date_of_birth = models.DateField(blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    avatar = models.ImageField(blank=True, null=True, upload_to="avatar")

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["date_of_birth", "first_name", "last_name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

## APP MODELS ##
class Professional(CustomUser):
    class Meta:
        verbose_name_plural = 'Professionals'
        verbose_name = 'Professional'

    title = models.CharField(max_length=200)

    def __str__(self):
        return self.get_full_name()
    
class Patient(CustomUser):
    class Meta:
        verbose_name_plural = 'Patients'
        verbose_name = 'Patient'

    prof_in_charge = models.ForeignKey(Professional, on_delete=models.CASCADE)
    social_sec_number = models.IntegerField(unique=True, null=False)

    def __str__(self):
        return self.get_full_name()
    
class ClinicalHistory(models.Model):
    class Meta:
        verbose_name_plural = 'Clinical Histories'
        verbose_name = 'Clinical History'
    
    name = models.CharField(max_length=100, blank=True, null=True)
    file = models.FileField(blank=True, upload_to="clinic", null=True)
    prof = models.ForeignKey(Professional, on_delete=models.SET_NULL, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name
    
class CalendarEvent(models.Model):
    class Meta:
        verbose_name = 'Calendar Event'
        verbose_name_plural = 'Calendar Events'

    name = models.CharField(max_length=100)
    start_time = models.DateTimeField(u'Starting time', auto_now=True)
    end_time = models.DateTimeField(u'End time', auto_now=True)
    description = models.CharField(max_length=500, blank=True)
    slug = models.SlugField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        super(CalendarEvent, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def check_overlap(self, fixed_start, fixed_end, new_start, new_end):
        overlap = False
        if new_start == fixed_end or new_end == fixed_start:    #edge case
            overlap = False
        elif (new_start >= fixed_start and new_start <= fixed_end) or (new_end >= fixed_start and new_end <= fixed_end): #innner limits
            overlap = True
        elif new_start <= fixed_start and new_end >= fixed_end: #outter limits
            overlap = True

        return overlap

    def get_absolute_url(self):
        return f"/calendar/{self.slug}"
    
    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError('Ending hour must be after the starting hour')

        events = CalendarEvent.objects.filter(day=self.day)
        if events.exists():
            for event in events:
                if self.check_overlap(event.start_time, event.end_time, self.start_time, self.end_time):
                    raise ValidationError(
                        'There is an overlap with another event: ' + str(event.name) + ', ' + str(
                            event.start_time) + '-' + str(event.end_time))


class Calendar(models.Model):
    class Meta:
        verbose_name = 'Calendar'
        verbose_name_plural = 'Calendars'

    cal_events = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, blank=True, null=True)
    prof = models.ForeignKey(Professional, on_delete=models.SET_NULL, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)
