from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError

ROLE_CHOICES = [
        ('doctor', 'Doctor'),
        ('assistant', 'Doctor\'s Assistant'),
        ('patient', 'Patient'),
]

## CUSTOM USER MODEL ##
class UserManager(BaseUserManager):
    def create_user(self, email, date_of_birth, first_name, last_name, password=None):
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
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
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
    avatar = models.ImageField(blank=True, null=True, upload_to="avatar", help_text='Avatar Image')

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
        return self.is_admin


## APP MODELS ##
class Staff(CustomUser):
    class Meta:
        verbose_name_plural = 'Staff Members'
        verbose_name = 'Staff'

    license = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.get_full_name()
    
class Patient(CustomUser):
    class Meta:
        verbose_name_plural = 'Patients'
        verbose_name = 'Patient'

    prof_in_charge = models.ForeignKey(Staff, on_delete=models.CASCADE, null=True, blank=True)
    social_sec_number = models.IntegerField(unique=True, null=False, help_text='Social Security Number')

    def __str__(self):
        return self.get_full_name()
    
class ClinicalHistory(models.Model):
    class Meta:
        verbose_name_plural = 'Clinical Histories'
        verbose_name = 'Clinical History'
    
    name = models.CharField(max_length=100, blank=True, null=True)
    file = models.FileField(blank=True, upload_to="clinic", null=True)
    prof = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True)
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
            raise ValidationError("The end time must be after the start time.")
        
        overlapping_events = CalendarEvent.objects.filter(
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(pk=self.pk)
        
        if overlapping_events.exists():
            overlap = overlapping_events.first()
            raise ValidationError(
                f"Overlap with event '{overlap.name}' from {overlap.start_time} to {overlap.end_time}."
            )

class Calendar(models.Model):
    class Meta:
        verbose_name = 'Calendar'
        verbose_name_plural = 'Calendars'

    cal_events = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, blank=True, null=True, related_name="calendars")
    prof = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name="calendars")
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True)

class Message(models.Model):
    sender = models.ForeignKey(
        Patient, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        help_text='The user sending the message.'
    )
    subject = models.CharField(
        max_length=255, 
        help_text='The subject of the message.'
    )
    content = models.TextField(
        help_text='The body of the message.'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='The time the message was sent.'
    )
    is_read = models.BooleanField(
        default=False,
        help_text='Whether the recipient has read the message.'
    )

    class Meta:
        ordering = ['-timestamp']  # Most recent messages first
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f"Message from {self.sender}: {self.subject}"
