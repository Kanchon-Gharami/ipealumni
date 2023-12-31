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
    SERIES_CHOICES.append(('faculty_member', 'Faculty Member'))
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

    MEMBERSHIP_CHOICES = [
        ('not_provided', 'Not Provided yet'),
        ('alumni_member', 'Alumni Member'),
        ('faculty_member', 'Faculty Member'),
        ('honorary_member', 'Honorary Member'),
        ('life_member', 'Life Member'),
    ]
    # attribute fields
    user = models.OneToOneField(MyCustomUser, on_delete=models.CASCADE, related_name='profile')
    roll = models.CharField(
        null=False, blank=False,
        max_length=7, 
        validators=[RegexValidator(r'^\d{1,7}$', message="Enter a valid roll number consisting of up to 7 digits.")],
        unique=True
    )
    series = models.CharField(max_length=20, choices=SERIES_CHOICES)
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

    membership = models.CharField(
        max_length=20, 
        choices=MEMBERSHIP_CHOICES, 
        default='not_provided'
    )

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
    phone_regex = RegexValidator(
        regex=r'^\+?([0-9]{1,3})?[-. ]?([0-9]{1,4})[-. ]?([0-9]{1,4})[-. ]?([0-9]{1,9})$',
        message="Enter a valid international phone number."
    )
    
    name = models.CharField(max_length=255, null=False, blank=False)
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)
    roll_number = models.CharField(
        null=False, blank=False,
        max_length=7, 
        validators=[RegexValidator(r'^\d{1,7}$', message="Enter a valid roll number consisting of up to 7 digits.")],
        unique=True
    )
    number_of_guests = models.IntegerField(
        null=True, blank=True, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(9)]
    )
    driver = models.IntegerField(
        null=True, blank=True, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(3)]
    )
    total_amount_paid = models.IntegerField(null=False, blank=False)
    upload_payment_slip = models.ImageField(upload_to='payment_slips/', null=True, blank=True)
    is_payment_varified = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    phone_no = models.CharField(
        validators=[phone_regex],
        max_length=18,
        null=True, blank=True
    )

    def __str__(self):
        return self.name


class Notice(models.Model):
    title = models.CharField(max_length=500, blank=False, null=False)
    paragraph = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='notice/', blank=True, null=True) 
    datetime_field = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    def __str__(self):
        return self.title

class Achievement(models.Model):
    title = models.CharField(max_length=500, blank=False, null=False)
    paragraph = models.TextField(blank=False, null=False)
    image = models.ImageField(upload_to='achievements/', blank=True, null=True)
    datetime_field = models.DateTimeField(auto_now_add=True, blank=False, null=False)

    def __str__(self):
        return self.title


class Carousel(models.Model):
    image = models.ImageField(upload_to='carousel_images/')  # you need to have Pillow installed to use ImageField
    quote = models.TextField()
    datetime_field = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.quote[:50]
    

class GalleryImage(models.Model):
    caption = models.CharField(max_length=255)
    image = models.ImageField(upload_to='gallery_images/')
    TAG_CHOICES = [
        ('first_reunion', 'First Reunion'),
        ('home_gallery', 'Home Gallery'),
    ]
    tag = models.CharField(max_length=20, choices=TAG_CHOICES)

    def __str__(self):
        return self.caption