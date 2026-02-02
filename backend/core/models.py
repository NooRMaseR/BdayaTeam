from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from imagekit.models import ProcessedImageField
from django.db import models

# Create your models here.
class BdayaUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not extra_fields.get("phone_number"):
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


class UserRole(models.TextChoices):
    MEMBER = "member"
    TECHNICAL = "technical"
    ORGANIZER = "organizer"
    

class Track(models.Model):
    track = models.CharField(max_length=40, unique=True)
    prefix = models.CharField(max_length=3, unique=True)
    description = models.TextField(blank=True, null=True)
    image = ProcessedImageField(upload_to="public/tracks", format="webP", null=True, blank=True) # type: ignore

    def __str__(self):
        return self.track
    
class TrackCounter(models.Model):
    track = models.OneToOneField(Track, on_delete=models.CASCADE)
    current_value = models.PositiveIntegerField(default=0)

class BdayaUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50)
    phone_number = PhoneNumberField(region="EG") # type: ignore
    role = models.CharField(max_length=15, choices=UserRole, default=UserRole.MEMBER)
    track = models.ForeignKey(Track, on_delete=models.SET_NULL, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    objects = BdayaUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username", "phone_number", "role"]
    
    @property
    def is_technical(self) -> bool:
        return self.role == UserRole.TECHNICAL
    
    @property
    def is_organizer(self) -> bool:
        return self.role == UserRole.ORGANIZER
    
    @property
    def is_member(self) -> bool:
        return self.role == UserRole.MEMBER
    
    def clean(self) -> None:
        if (self.is_technical or self.is_member) and self.track is None:
            raise ValidationError(f"Track is requeired for {self.role} role")
        elif self.is_organizer and self.track:
            raise ValidationError(f"{self.role} cannot have a track")
        return super().clean()

    def __str__(self):
        return self.username
