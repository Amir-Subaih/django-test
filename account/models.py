from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class TypeUser(models.TextChoices):
    EMPLOYER = "Employer", "Employer"
    APPLICANT = "Applicant", "Applicant"
    OTHER = "Other", "Other"


class AccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('isAdmin', True)

        if extra_fields.get('isAdmin') is not True:
            raise ValueError("Superuser must have isAdmin=True")

        return self.create_user(email, username, password, **extra_fields)

class Account(AbstractBaseUser):
    username = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Make sure to use a longer length
    user_type = models.CharField(max_length=30, choices=TypeUser.choices, default=TypeUser.APPLICANT)
    isAdmin = models.BooleanField(default=False)

    objects = AccountManager()

    USERNAME_FIELD = 'email'  # Use 'email' for authentication
    REQUIRED_FIELDS = ['username']  # Fields required when creating a superuser

    def __str__(self):
        return self.email



class Profile(models.Model):
    account = models.OneToOneField(Account, related_name='profile', on_delete=models.CASCADE)  # Use Account instead of User
    reset_password_token = models.CharField(max_length=50, blank=True, default='')
    reset_password_expire = models.DateTimeField(null=True, blank=True)

@receiver(post_save, sender=Account)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(account=instance)  # Create Profile when Account is created
