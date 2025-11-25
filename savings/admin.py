from django.contrib import admin
from .models import SavingsAccount, Contribution

@admin.register(SavingsAccount)
class SavingsAccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'member', 'balance', 'created_at')


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    list_display = ('account', 'amount', 'status', 'payment_method', 'created_at')
    list_filter = ('status',)
