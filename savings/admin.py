from django.contrib import admin
#from .models import SavingsAccount, DepositRequest, Transaction
from decimal import Decimal
from django.contrib import messages
from django.db import transaction

@admin.action(description="Manually credit selected accounts")
def admin_credit(modeladmin, request, queryset):
    # opens a confirmation page in real project; here we credit a fixed amount for demo
    for acc in queryset:
        try:
            acc.deposit(Decimal('1000.00'), description='Admin credit', created_by=request.user)
        except Exception as e:
            messages.error(request, f"Error crediting {acc}: {e}")
    messages.success(request, "Selected accounts credited (demo amount).")

@admin.action(description="Manually debit selected accounts")
def admin_debit(modeladmin, request, queryset):
    for acc in queryset:
        try:
            acc.withdraw(Decimal('100.00'), description='Admin debit', created_by=request.user)
        except Exception as e:
            messages.error(request, f"Error debiting {acc}: {e}")
    messages.success(request, "Selected accounts debited (demo amount).")

# @admin.register(SavingsAccount)
# class SavingsAccountAdmin(admin.ModelAdmin):
#     list_display = ('member', 'account_number', 'balance', 'created_at')
#     search_fields = ('member__user__username', 'account_number')
#     actions = [admin_credit, admin_debit]

# @admin.register(DepositRequest)
# class DepositRequestAdmin(admin.ModelAdmin):
#     list_display = ('account', 'amount', 'status', 'created_at', 'processed_at')
#     list_filter = ('status', 'created_at')
#     actions = ['approve_selected', 'reject_selected']

#     def approve_selected(self, request, queryset):
#         for dr in queryset:
#             try:
#                 dr.mark_confirmed(processed_by=request.user)
#             except Exception as e:
#                 self.message_user(request, f"Error: {e}", level=messages.ERROR)
#     approve_selected.short_description = "Confirm selected deposits"

#     def reject_selected(self, request, queryset):
#         for dr in queryset:
#             dr.mark_rejected(processed_by=request.user)
#     reject_selected.short_description = "Reject selected deposits"

# @admin.register(Transaction)
# class TransactionAdmin(admin.ModelAdmin):
#     list_display = ('account', 'tx_type', 'amount', 'balance_after', 'created_at', 'created_by')
#     search_fields = ('account__member__user__username', 'reference')
#     list_filter = ('tx_type',)
