from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Loan, LoanRepayment
from .forms import LoanApplicationForm
from transactions.models import Transaction
from decimal import Decimal


@login_required
def loan_dashboard(request):
    loans = request.user.memberprofile.loans.all().order_by('-applied_at')
    total_loans = sum([loan.total_payable() for loan in loans if loan.status in ['Approved', 'Pending']])
    context = {
        'loans': loans,
        'total_loans': total_loans,
    }
    return render(request, 'loans/dashboard.html', context)


@login_required
def apply_loan(request):
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
    loan = Loan.objects.get(id=loan_id, member=request.user.memberprofile)

    if loan.status != 'Approved':
        messages.error(request, "You can only repay approved loans.")
        return redirect('dashboard')

    # Calculate outstanding
    total_repaid = sum([r.amount for r in loan.repayments.all()])
    outstanding = loan.total_payable() - Decimal(total_repaid)

    if request.method == "POST":
        amount = Decimal(request.POST.get("amount"))
        if amount <= 0:
            messages.error(request, "Repayment amount must be greater than zero.")
            return redirect('repay_loan', loan_id=loan.id)

        if amount > outstanding:
            messages.error(request, f"Cannot repay more than outstanding: {outstanding}")
            return redirect('repay_loan', loan_id=loan.id)

        # Deduct from savings
        account = loan.savings_account
        if amount > account.balance:
            messages.error(request, "Insufficient savings balance to make repayment.")
            return redirect('repay_loan', loan_id=loan.id)

        account.balance -= amount
        account.save()

        # Create transaction
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

        # Check if loan is fully repaid
        if amount == outstanding:
            loan.status = 'Paid'
            loan.save()

        messages.success(request, f"Repayment of UGX {amount} successful.")
        return redirect('dashboard')

    context = {
        'loan': loan,
        'outstanding': outstanding
    }
    return render(request, 'loans/repay_loan.html', context)
