from django.db import transaction
from savings.models import Contribution

def confirm_contribution(contribution):
    """
    Confirm a contribution and update the linked SavingsAccount balance
    """
    with transaction.atomic():
        contribution.status = "Confirmed"
        contribution.save()

        account = contribution.account
        account.balance += contribution.amount
        account.save()

    return account.balance
