from decimal import Decimal
from django import forms
#from .models import DepositRequest


class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2)
    stripe_token = forms.CharField(widget=forms.HiddenInput())
