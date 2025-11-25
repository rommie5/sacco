from transactions.models import Transaction
from django.db import models
from django.utils import timezone
from users.models import MemberProfile
from savings.models import SavingsAccount
from decimal import Decimal

class Loan(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Paid', 'Paid'),
    )

    member = models.ForeignKey(MemberProfile, on_delete=models.CASCADE, related_name='loans')
    savings_account = models.ForeignKey(SavingsAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.0)  # %
    term_months = models.PositiveIntegerField(default=12)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    applied_at = models.DateTimeField(default=timezone.now)
    approved_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    reason_declined = models.TextField(null=True, blank=True)

    def total_payable(self):
        """Calculate total amount including interest."""
        return self.amount + (self.amount * self.interest_rate / Decimal(100))

    def __str__(self):
        return f"{self.member.full_name} - {self.amount} ({self.status})"



class LoanRepayment(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='repayments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(default=timezone.now)
    transaction = models.OneToOneField(Transaction, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.loan.member.full_name} - {self.amount}"
