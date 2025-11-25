from django.db import models
from django.utils import timezone
from users.models import MemberProfile

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('Deposit', 'Deposit'),
        ('Withdrawal', 'Withdrawal'),
        ('Loan Payment', 'Loan Payment'),
        ('Loan Disbursement', 'Loan Disbursement'),
    )

    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    gateway_ref = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=30, default='Initiated')  # Initiated, Success, Failed
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.member.user.username} - {self.transaction_type} - {self.amount}"
