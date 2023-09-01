from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import UserManager as DefaultUserManager

class CustomUserManager(DefaultUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class MyCustomUser(AbstractUser):
    username = models.CharField(max_length=30, unique=False, blank=True, null=True)  # Overriding
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)
    name = models.CharField(max_length=200, blank=False, null=False)
    is_admin = models.BooleanField(default=False)
    is_alumni = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

# Create profile model
class Profile(models.Model):
    # Choice fields
    SERIES_CHOICES = [(str(year), str(year)) for year in range(2005, 2017)]
    phone_regex = RegexValidator(
        regex=r'^\+?([0-9]{1,3})?[-. ]?([0-9]{1,4})[-. ]?([0-9]{1,4})[-. ]?([0-9]{1,9})$',
        message="Enter a valid international phone number."
    )
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    MARITAL_STATUS_CHOICES = [('married', 'Married'), ('single', 'Single')]

    # attribute fields
    user = models.OneToOneField(MyCustomUser, on_delete=models.CASCADE, related_name='profile')
    roll = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(9999999)])
    series = models.CharField(max_length=4, choices=SERIES_CHOICES)
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=18,
    )
    whatsapp_no = models.CharField(max_length=15, validators=[RegexValidator(r'^\d{10,15}$')], blank=True, null=True)
    current_position = models.CharField(max_length=100)
    current_organization = models.CharField(max_length=100)
    previous_experience = models.TextField(null=True, blank=True)
    certificate = models.TextField(null=True, blank=True)
    skills = models.TextField(null=True, blank=True)
    present_address = models.TextField()
    home_district = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    marital_status = models.CharField(max_length=7, choices=MARITAL_STATUS_CHOICES, null=True, blank=True)
    linkedin = models.URLField(max_length=200, blank=True, null=True)
    facebook = models.URLField(max_length=200, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/')

    # HigherEducation
    name_of_degree1 = models.CharField(max_length=100, blank=True, null=True)
    institution1 = models.CharField(max_length=100, blank=True, null=True)
    name_of_degree2 = models.CharField(max_length=100, blank=True, null=True)
    institution2 = models.CharField(max_length=100, blank=True, null=True)
    name_of_degree3 = models.CharField(max_length=100, blank=True, null=True)
    institution3 = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.name}'s Profile"
    

class ReunionRegistration(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)
    roll_number = models.IntegerField(
        null=False, blank=False,
        validators=[MinValueValidator(0), MaxValueValidator(9999999)]
    )
    number_of_guests = models.IntegerField(
        null=False, blank=False,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    driver = models.IntegerField(
        null=False, blank=False,
        validators=[MinValueValidator(1), MaxValueValidator(3)]
    )
    total_amount_paid = models.IntegerField(null=False, blank=False)
    upload_payment_slip = models.ImageField(upload_to='payment_slips/', null=False, blank=False)
    is_payment_varified = models.BooleanField(default=False)

    def __str__(self):
        return self.name

