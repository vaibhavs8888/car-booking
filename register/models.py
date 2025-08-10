from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)




class Car(models.Model):
    car_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default="Pune", editable=False)
    image = models.ImageField(upload_to='cars/', blank=True, null=True)
    is_booked = models.BooleanField(default=False)
    available_from = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.car_name} ({self.city})"


class MyUserManager(BaseUserManager):
    def create_user(self, Email, Name, Mobile_no, Date_Of_Birth, password=None, **extra_fields):
        if not Email:
            raise ValueError('Users must have an email address')

        user = self.model(
            Email=self.normalize_email(Email),
            Name=Name,
            Mobile_no=Mobile_no,
            Date_Of_Birth=Date_Of_Birth,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, Email, Name, Mobile_no, Date_Of_Birth, password=None, **extra_fields):
        user = self.create_user(
            Email=Email,
            Name=Name,
            Mobile_no=Mobile_no,
            Date_Of_Birth=Date_Of_Birth,
            password=password,
            **extra_fields
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class registermodel(AbstractBaseUser):
    # existing fields
    Email = models.EmailField(verbose_name='email address', max_length=100, unique=True)
    Name = models.CharField(max_length=200)
    Date_Of_Birth = models.DateField()
    Mobile_no = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    booked_car = models.OneToOneField(
        'register.Car',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='booked_by_user'
    )

    # ➕ Add these fields
    pickup_datetime = models.DateTimeField(null=True, blank=True)
    dropoff_datetime = models.DateTimeField(null=True, blank=True)

    # other existing methods
    objects = MyUserManager()
    USERNAME_FIELD = 'Email'
    REQUIRED_FIELDS = ['Name','Mobile_no','Date_Of_Birth']

    def __str__(self):
        return self.Email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
    

class Booking(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    user = models.ForeignKey(registermodel, on_delete=models.CASCADE)
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    dropoff_date = models.DateField()
    dropoff_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Document fields with consistent upload paths
    driving_licence = models.FileField(upload_to='documents/%Y/%m/%d/driving_licence/')
    residence_proof = models.FileField(upload_to='documents/%Y/%m/%d/residence_proof/')
    pan_card = models.FileField(upload_to='documents/%Y/%m/%d/pan_card/')
    aadhaar_card = models.FileField(upload_to='documents/%Y/%m/%d/aadhaar_card/')
    payment_screenshot = models.ImageField(upload_to='documents/%Y/%m/%d/payment/')

    def __str__(self):
        return f"{self.car.car_name} booked by {self.user}"
    
    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"



