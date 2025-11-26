from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render, redirect,HttpResponse
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .models import SavingsAccount, Contribution
from Kinna.services import confirm_contribution
from transactions.stripe_gateway import StripeGateway
from transactions.models import Transaction
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY
gateway = StripeGateway()
from .models import SavingsAccount, Contribution

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def deposit_view(request):
    try:
        account = request.user.memberprofile.savings_account
    except SavingsAccount.DoesNotExist:
        messages.error(request, "No savings account found. Contact admin.")
        return redirect('dashboard')

    if request.method == "POST":
        amount = request.POST.get("amount")
        try:
            amount_decimal = Decimal(amount)
            if amount_decimal <= 0:
                raise ValueError("Amount must be greater than 0")
        except Exception as e:
            messages.error(request, f"Invalid amount: {e}")
            return redirect("deposit")

        # Convert to cents for Stripe
        amount_cents = int(amount_decimal * 100)

        # Create Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": amount_cents,
                    "product_data": {
                        "name": f"Deposit for {account.account_number}",
                    },
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.build_absolute_uri("/savings/deposit/success/") + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=request.build_absolute_uri("/savings/deposit/"),
            metadata={
                "account_id": account.id,
                "user_id": request.user.id
            }
        )

        Contribution.objects.create(
        account=account,
        amount=amount_decimal,
        payment_method="Stripe",
        status="Pending"
        )


        return redirect(session.url)

    return render(request, "savings/deposit.html", {"account": account, "stripe_key": settings.STRIPE_PUBLIC_KEY})

@login_required
def deposit_history_view(request):
    profile = request.user.memberprofile
    try:
        account = profile.savings_account
    except SavingsAccount.DoesNotExist:
        messages.error(request, "No savings account found. Contact admin.")
        return redirect('dashboard')

    contributions = Contribution.objects.filter(account=account).order_by('-created_at')

    context = {
        'contributions': contributions,
    }
    return render(request, 'savings/deposit_history.html', context)
# Succes View for Deposit
from decimal import Decimal

@login_required
def deposit_success(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        return redirect("deposit")  # user accessed directly

    # Retrieve the session from Stripe
    session = stripe.checkout.Session.retrieve(session_id)

    # Convert to Decimal
    amount = Decimal(session.amount_total) / 100  # amount_total is in cents

    # Update user's account
    account = request.user.memberprofile.savings_account
    account.balance += amount  # now safe
    account.save()

    return render(request, "savings/deposit_success.html", {
        "account": account,
        "amount": amount,
    })



@csrf_exempt
def stripe_webhook(request):
    import stripe
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = "whsec_..."

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        contribution_id = session["metadata"]["contribution_id"]
        account_id = session["metadata"]["account_id"]

        amount = Decimal(session["amount_total"]) / Decimal(100)

        # Update the specific contribution
        contribution = Contribution.objects.filter(
            account=account,
            amount=amount,
            status="Pending"
        ).order_by('-created_at').first()

        contribution.status = "CONFIRMED"
        contribution.save()

        # Update balance
        account = SavingsAccount.objects.get(id=account_id)
        account.balance += amount
        account.save()

    return HttpResponse(status=200)

# Account
from django.db.models import Sum
from decimal import Decimal

@login_required
def account_view(request):
    """Display the member's savings account details"""
    profile = request.user.memberprofile

    # Get the linked savings account (if exists)
    try:
        savings_account = profile.savings_account
    except SavingsAccount.DoesNotExist:
        savings_account = None

    # Recent contributions (latest 5)
    contributions = Contribution.objects.filter(account__member=profile).order_by('-created_at')[:5]

    # If user has no savings account yet, prevent crashes
    if savings_account:
        total_balance = savings_account.balance
    else:
        total_balance = Decimal('0')

    # Sum confirmed contributions only
    total_contributions = (
        Contribution.objects.filter(account__member=profile, status="Confirmed")
        .aggregate(total=Sum('amount'))['total'] or Decimal('0')
    )

    context = {
        'profile': profile,
        'savings_account': savings_account,
        'contributions': contributions,
        'total_balance': total_balance,
        'total_contributions': total_contributions,
    }
    return render(request, 'savings/account.html', context)

@login_required
def dashboard(request):
    profile = request.user.memberprofile

    # Try get savings account
    try:
        savings_account = profile.savings_account
        total_balance = savings_account.balance
    except SavingsAccount.DoesNotExist:
        savings_account = None
        total_balance = 0

    # Get contributions (limit recent 5)
    contributions = Contribution.objects.filter(
        account__member=profile
    ).order_by('-created_at')[:5]

    # Sum all confirmed contributions
    total_contributions = contributions.aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        "profile": profile,
        "savings_account": savings_account,
        "total_balance": total_balance,
        "total_contributions": total_contributions,
        "contributions": contributions,
    }

    return render(request, "users/dashboard.html", context)
@login_required
def transaction_history_view(request):
    profile = request.user.memberprofile
    transactions = Transaction.objects.filter(member=profile).order_by('-created_at')

    context = {
        'transactions': transactions,
    }
    return render(request, 'users/transaction_history.html', context)
