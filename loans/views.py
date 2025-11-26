from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Loan, LoanRepayment
from .forms import LoanApplicationForm
from transactions.models import Transaction


@login_required
def loan_dashboard(request):
    """Displays the user's loans and total obligations."""
    loans = request.user.memberprofile.loans.all().order_by('-applied_at')
    total_loans = sum([loan.total_payable() for loan in loans if loan.status in ['Approved', 'Pending']])
    context = {
        'loans': loans,
        'total_loans': total_loans,
    }
    return render(request, 'loans/dashboard.html', context)


@login_required
def apply_loan(request):
    """Allows a user to apply for a loan if they have a savings account."""
    try:
        savings_account = request.user.memberprofile.savings_account
    except Exception:
        messages.error(request, "You must have a savings account to apply for a loan.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoanApplicationForm(request.POST, savings_account=savings_account)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.member = request.user.memberprofile
            loan.savings_account = savings_account
            loan.save()
            messages.success(request, "Loan application submitted successfully!")
            return redirect('loans:dashboard')
    else:
        form = LoanApplicationForm(savings_account=savings_account)

    return render(request, 'loans/apply.html', {'form': form})


@login_required
def repay_loan_view(request, loan_id):
    """Handles repayment for a single approved loan."""
    loan = get_object_or_404(Loan, id=loan_id, member=request.user.memberprofile)

    if loan.status != 'Approved':
        messages.error(request, "Only approved loans can be repaid.")
        return redirect('dashboard')

    # Calculate outstanding balance
    total_repaid = loan.repayments.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    outstanding = loan.total_payable() - total_repaid

    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get("amount"))
        except:
            messages.error(request, "Invalid repayment amount.")
            return redirect('repay_loan', loan_id=loan.id)

        if amount <= 0:
            messages.error(request, "Repayment amount must be greater than zero.")
            return redirect('repay_loan', loan_id=loan.id)

        if amount > outstanding:
            messages.error(request, f"You cannot pay more than UGX {outstanding}.")
            return redirect('repay_loan', loan_id=loan.id)

        account = loan.savings_account
        if amount > account.balance:
            messages.error(request, "Insufficient savings balance for this repayment.")
            return redirect('repay_loan', loan_id=loan.id)

        # Deduct funds and save
        account.balance -= amount
        account.save()

        # Create transaction record
        transaction = Transaction.objects.create(
            member=request.user.memberprofile,
            amount=amount,
            transaction_type="Loan Payment",
            status="Success"
        )

        # Create repayment record
        LoanRepayment.objects.create(
            loan=loan,
            amount=amount,
            transaction=transaction
        )

        # Close loan if fully repaid
        if outstanding == amount:
            loan.status = 'Paid'
            loan.save()

        messages.success(request, f"UGX {amount} has been successfully repaid.")
        return redirect('dashboard')

    context = {
        'loan': loan,
        'outstanding': outstanding
    }
    return render(request, 'loans/repay_loan.html', context)
