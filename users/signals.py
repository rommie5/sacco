import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import MemberProfile
from savings.models import SavingsAccount

def generate_account_number():
    """Generates a unique 12-digit SACCO account number."""
    while True:
        account_number = str(uuid.uuid4().int)[:12]
        if not SavingsAccount.objects.filter(account_number=account_number).exists():
            return account_number

User = settings.AUTH_USER_MODEL

@receiver(post_save, sender=User)
def create_profile_and_savings(sender, instance, created, **kwargs):
    if created:
        # Create MemberProfile if it doesn't exist
        profile, _ = MemberProfile.objects.get_or_create(user=instance)

        # Create SavingsAccount if it doesn't exist
        SavingsAccount.objects.get_or_create(
            member=profile,
            defaults={'account_number': generate_account_number()}
        )
