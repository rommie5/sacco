from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import SavingsAccount
from users.models import MemberProfile
import secrets

@receiver(post_save, sender=MemberProfile)
def create_account_on_approval(sender, instance, created, **kwargs):
    """
    When member profile becomes is_approved=True ensure they have a savings account.
    """
    # Only trigger when newly approved or first creation but approved
    if instance.is_approved:
        # create if not exists
        SavingsAccount.objects.get_or_create(member=instance, defaults={
            'account_number': f"SACCO{secrets.token_hex(8).upper()}"
        })
