from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings


MARITAL_CHOICES = [
    ('single', 'Single'),
    ('married', 'Married'),
    ('divorced', 'Divorced'),
    ('widowed', 'Widowed'),
]

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_admin=models.BooleanField(default=False)
    is_member=models.BooleanField(default=False)
    is_auditor =models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username}({'Admin' if self.is_admin else 'Member'})"
    

class MemberProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberprofile')

    # Member Details
    surname = models.CharField(max_length=100)
    other_name = models.CharField(max_length=100, blank=True, null=True)
    given_name = models.CharField(max_length=100)
    area_of_residence = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_CHOICES, default='single')
    phone_number = models.CharField(max_length=20)

    # ID Upload
    passport_photo = models.ImageField(upload_to='member_photos/', blank=True, null=True)

    # Parent Info
    mother_name = models.CharField(max_length=120, blank=True, null=True)
    father_name = models.CharField(max_length=120, blank=True, null=True)
    parents_contact = models.CharField(max_length=20, blank=True, null=True)

    # Next of Kin Info
    nok_name = models.CharField("Next of Kin name", max_length=120, blank=True, null=True)
    nok_relationship = models.CharField(max_length=120, blank=True, null=True)
    nok_contact = models.CharField(max_length=20, blank=True, null=True)
    nok_address = models.CharField(max_length=255, blank=True, null=True)
    nok_date_of_birth = models.DateField(blank=True, null=True)

    # Approval Logic
    is_completed = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)  # admin approval flag

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f"{self.given_name} {self.surname}"

    def __str__(self):
        return f"MemberProfile({self.user.username})"

class Document(models.Model):
        member=models.ForeignKey(MemberProfile,on_delete=models.CASCADE,related_name="documents")
        doc_type=models.CharField(max_length=50)
        file=models.FileField(upload_to='documents/')
        verified=models.BooleanField(default=False)
        uploaded_at=models.DateTimeField(default=timezone.now)

        def __str__(self):
            return f"{self.doc_type} for {self.member.user.username}"