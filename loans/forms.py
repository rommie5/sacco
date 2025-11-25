from django import forms
from .models import Loan

class LoanApplicationForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['amount', 'interest_rate', 'term_months']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000'}),
            'interest_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'term_months': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.savings_account = kwargs.pop('savings_account', None)
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.savings_account and amount > self.savings_account.balance:
            raise forms.ValidationError("Loan cannot exceed your current savings.")
        if amount <= 0:
            raise forms.ValidationError("Loan amount must be greater than zero.")
        return amount
