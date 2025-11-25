from django.utils import timezone
from django.contrib import admin
from django.contrib import messages
from .models import Loan
from transactions.models import Transaction

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'status', 'applied_at', 'approved_at', 'declined_at')
    list_filter = ('status',)
    actions = ['approve_loans', 'decline_loans']

    def approve_loans(self, request, queryset):
        approved_count = 0

        for loan in queryset.filter(status='Pending'):
            account = loan.savings_account

            if not account:
                messages.error(request, f"Loan for {loan.member} skipped: No savings account attached.")
                continue

            # 1. Update loan
            loan.status = 'Approved'
            loan.approved_at = timezone.now()
            loan.save()

            # 2. Update member balance
            account.balance += loan.amount
            account.save()

            # 3. Create transaction record
            Transaction.objects.create(
                member=loan.member,
                amount=loan.amount,
                transaction_type='Loan Disbursement',
                status='Success',
                created_at=timezone.now(),
            )

            approved_count += 1

        self.message_user(request, f"{approved_count} loan(s) approved and transactions recorded.")

    approve_loans.short_description = "Approve selected loans"

    def decline_loans(self, request, queryset):
        declined_count = 0

        for loan in queryset.filter(status='Pending'):
            loan.status = 'Rejected'
            loan.declined_at = timezone.now()
            loan.save()
            declined_count += 1

        self.message_user(request, f"{declined_count} loan(s) declined.")

    decline_loans.short_description = "Decline selected loans"
