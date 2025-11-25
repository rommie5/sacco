# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import MemberProfile
from savings.models import SavingsAccount
import random

User = get_user_model()

def generate_account_number():
    return "SAC" + str(random.randint(10000000, 99999999))

@receiver(post_save, sender=User)
def create_member_profile_and_savings(sender, instance, created, **kwargs):
    if created:
        # Create MemberProfile
        profile = MemberProfile.objects.create(user=instance)

        # Create SavingsAccount for the member
        SavingsAccount.objects.create(
            member=profile,
            account_number=generate_account_number()
        )
