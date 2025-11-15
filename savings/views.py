from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SavingsAccount, Deposit, Transaction
import stripe

stripe.api_key = "YOUR_STRIPE_SECRET_KEY"

@login_required
def dashboard(request):
    account = getattr(request.user, 'savings_account', None)
    return render(request, 'savings/dashboard.html', {'account': account})

@login_required
def deposit(request):
    account = getattr(request.user, 'savings_account', None)
    if not account:
        messages.error(request, "Savings account not found.")
        return redirect('dashboard')

    if request.method == 'POST':
        token = request.POST.get('stripeToken')
        amount = request.POST.get('amount')

        if not token or not amount:
            messages.error(request, "Payment info missing.")
            return redirect('savings_deposit')

        try:
            amount = float(amount)

            # Create Stripe charge
            charge = stripe.Charge.create(
                amount=int(amount * 100),
                currency='usd',
                source=token,
                description=f"Deposit to {account.user.username}'s Savings"
            )

            # Update account balance
            account.balance += amount
            account.save()

            # Log deposit and transaction
            Deposit.objects.create(account=account, amount=amount, stripe_charge_id=charge.id)
            Transaction.objects.create(
                account=account,
                transaction_type='deposit',
                amount=amount,
                balance_after=account.balance,
                stripe_charge_id=charge.id,
                description="Deposit via Stripe"
            )

            messages.success(request, f"Deposit of ${amount} successful!")
            return redirect('savings_dashboard')

        except stripe.error.StripeError as e:
            messages.error(request, f"Stripe error: {str(e)}")
            return redirect('savings_deposit')

    return render(request, 'savings/deposit.html', {'account': account})
