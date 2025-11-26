from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from .forms import UserRegistrationForm, UserLoginForm, CompleteProfileForm
from .models import MemberProfile
from savings.models import SavingsAccount
import uuid
from savings.models import SavingsAccount, Contribution
from users.models import MemberProfile
from django.db.models import Sum
from django.db import models
from loans.models import Loan, LoanRepayment
from decimal import Decimal
from transactions.models import Transaction


# -----------------------
# Registration
# -----------------------
from django.db import transaction

def generate_account_number():
    """Generates a unique 12-digit SACCO account number."""
    while True:
        account_number = str(uuid.uuid4().int)[:12]
        if not SavingsAccount.objects.filter(account_number=account_number).exists():
            return account_number
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Save user
                user = form.save(commit=False)
                user.is_member = True
                user.is_admin = False
                user.is_auditor = False
                user.save()

                # Create MemberProfile and SavingsAccount safely
                profile, _ = MemberProfile.objects.get_or_create(user=user)
                SavingsAccount.objects.get_or_create(
                    member=profile,
                    defaults={'account_number': generate_account_number()}
                )

            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})
# -----------------------
# Login with profile checks
# -----------------------


def login_view(request):
    form = UserLoginForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)

        # Ensure member profile exists
        profile, created = MemberProfile.objects.get_or_create(user=user)

        # Ensure linked savings account exists
        if created or not hasattr(profile, 'savings_account'):
            from savings.models import SavingsAccount
            from users.views import generate_account_number
            SavingsAccount.objects.create(
                member=profile,
                account_number=generate_account_number()
            )

        # Incomplete profile → redirect to complete profile
        if not profile.is_completed:
            messages.warning(request, "Please complete your profile to access the SACCO dashboard.")
            return redirect('completeprofile')

        # Waiting admin approval
        if not profile.is_approved:
            return redirect('pending_approval')

        # Approved → dashboard
        return redirect('dashboard')

    return render(request, 'registration/login.html', {'form': form})


# -----------------------
# Pending approval view
# -----------------------
@login_required
def pending_approval(request):
    profile = request.user.memberprofile

    # If already approved, redirect to dashboard
    if profile.is_approved:
        return redirect('dashboard')

    return render(request, 'users/pending.html', {'profile': profile})


# -----------------------
# Admin dashboard
# -----------------------
@login_required
def admin_dashboard(request):
    context = {
        "pending_approvals": MemberProfile.objects.filter(is_approved=False).count(),
        "active_members": MemberProfile.objects.filter(is_approved=True).count(),
    }
    return render(request, "users/admin.html", context)


# -----------------------
# User dashboard
# -----------------------
@login_required
def dashboard_view(request):
    profile = request.user.memberprofile

    try:
        savings_account = profile.savings_account
        total_balance = savings_account.balance

        contributions = Contribution.objects.filter(account__member=profile)
        total_contributions = contributions.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')

        # Outstanding loan
        loans = Loan.objects.filter(member=profile, status='Approved')
        active_loan = loans.first()

        total_loans = sum([loan.total_payable() for loan in loans], Decimal('0.00'))
        repayments = LoanRepayment.objects.filter(loan__member=profile)
        total_repaid = sum([r.amount for r in repayments], Decimal('0.00'))
        outstanding_loan_balance = total_loans - total_repaid

    except SavingsAccount.DoesNotExist:
        savings_account = None
        total_balance = Decimal('0.00')
        contributions = []
        total_contributions = Decimal('0.00')
        outstanding_loan_balance = Decimal('0.00')
        active_loan = None

    context = {
        'profile': profile,
        'savings_account': savings_account,
        'total_balance': total_balance,
        'total_contributions': total_contributions,
        'contributions': contributions.order_by('-created_at')[:5],
        'outstanding_loan_balance': outstanding_loan_balance,
        'active_loan': active_loan,
    }

    return render(request, 'users/dashboard.html', context)

#repay loan 
@login_required
def repay_loan(request, loan_id):
    loan = get_object_or_404(Loan, id=loan_id, member=request.user.memberprofile)

    if request.method == "POST":
        amount = Decimal(request.POST.get("amount"))
        LoanRepayment.objects.create(loan=loan, amount=amount)

        return redirect("dashboard")

    context = {
        "loan": loan
    }
    return render(request, "loans/repay_loan.html", context)
# -----------------------
# Complete member profile
# -----------------------
@login_required
def completeprofile(request):
    profile, created = MemberProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CompleteProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.is_completed = True
            profile.is_approved = False  # Must wait for admin approval
            profile.save()
            messages.success(request, "Profile submitted! Waiting for approval.")
            return redirect('pending_approval')
    else:
        form = CompleteProfileForm(instance=profile)

    return render(request, 'users/completeprofile.html', {'form': form})


# -----------------------
# Logout
# -----------------------
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# -----------------------
# Profile view
# -----------------------
@login_required
def profile_view(request):
    profile, created = MemberProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "national_id": "N/A",
            "phone_number": "N/A",
            "address": "",
            "membership_status": "Pending"
        }
    )
    return render(request, 'users/profile.html', {'profile': profile})


@login_required
def transaction_history_view(request):
    profile = request.user.memberprofile
    transactions = Transaction.objects.filter(member=profile).order_by('-created_at')

    context = {
        'transactions': transactions,
    }
    return render(request, 'users/transaction_history.html', context)
