from django.db import models
from django.utils import timezone
from users.models import MemberProfile
from transactions.models import Transaction
import uuid

def generate_account_number():
    return str(uuid.uuid4())[:50]  # 50 chars max

class SavingsAccount(models.Model):
    member = models.OneToOneField(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name='savings_account'
    )
    account_number = models.CharField(max_length=50, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.member.user.username} - {self.account_number}"
    
    
class Contribution(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Failed', 'Failed'),
    )

    account = models.ForeignKey(SavingsAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, default="Stripe")
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.account.account_number} - {self.amount} ({self.status})"
