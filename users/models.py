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

# -----------------------
# Custom User Model
# -----------------------
class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_member = models.BooleanField(default=False)
    is_auditor = models.BooleanField(default=False)

    def __str__(self):
        role = 'Admin' if self.is_admin else 'Member' if self.is_member else 'Auditor'
        return f"{self.username} ({role})"

    # Convenience property to access member profile
    @property
    def member_profile(self):
        return getattr(self, 'memberprofile', None)

    # Convenience property to access savings account through profile
    @property
    def savings_account(self):
        profile = self.member_profile
        if profile:
            return getattr(profile, 'savingsaccount', None)
        return None

    # Total confirmed contributions
    @property
    def total_contributions(self):
        account = self.savings_account
        if account:
            return account.contributions.filter(status='Confirmed').aggregate(total=models.Sum('amount'))['total'] or 0
        return 0


# -----------------------
# Member Profile Model
# -----------------------
class MemberProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberprofile')

    # Personal Details
    surname = models.CharField(max_length=100)
    other_name = models.CharField(max_length=100, blank=True, null=True)
    given_name = models.CharField(max_length=100)
    area_of_residence = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_CHOICES, default='single')
    phone_number = models.CharField(max_length=20)

    # ID Upload / Passport Photo
    passport_photo = models.ImageField(upload_to='member_photos/', blank=True, null=True)

    # Parent Info
    mother_name = models.CharField(max_length=120, blank=True, null=True)
    father_name = models.CharField(max_length=120, blank=True, null=True)
    parents_contact = models.CharField(max_length=20, blank=True, null=True)

    # Next of Kin
    nok_name = models.CharField("Next of Kin Name", max_length=120, blank=True, null=True)
    nok_relationship = models.CharField(max_length=120, blank=True, null=True)
    nok_contact = models.CharField(max_length=20, blank=True, null=True)
    nok_address = models.CharField(max_length=255, blank=True, null=True)
    nok_date_of_birth = models.DateField(blank=True, null=True)

    # Approval / Status
    is_completed = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)  # Must be approved by admin

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f"{self.given_name} {self.surname}"

    def __str__(self):
        return f"{self.full_name()} ({self.user.username})"


# -----------------------
# Member Documents
# -----------------------
class Document(models.Model):
    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=50)  # e.g., "ID", "Certificate"
    file = models.FileField(upload_to='documents/')
    verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.doc_type} for {self.member.full_name()}"
