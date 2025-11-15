from django import forms
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from .models import User,MemberProfile

class UserRegistrationForm(UserCreationForm):
    email=forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class':'form-control',
            'placeholder':'Email Address',
        })
    )
    username=forms.CharField(
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'Username',
        })
    )
    password1=forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':'form-control',
            'placeholder':'Password',
        })
    )
    password2=forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':'form-control',
            'placeholder':'Confirm Password',
        })
    )

    class Meta:
        model=User
        fields=['username','email','password1','password2']

class UserLoginForm(AuthenticationForm):
    username=forms.CharField(
        widget=forms.TextInput(attrs={
            'class':'form-control',
            'placeholder':'Username',
        })
    )
    password=forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class':'form-control',
            'placeholder':'Password',
        })
    )
    class Meta:
        model=User
        fields=['username','password']
 

class CompleteProfileForm(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = [
            # Member Details
            'surname', 'other_name', 'given_name', 'area_of_residence',
            'date_of_birth', 'marital_status', 'phone_number',
            'passport_photo',
            'mother_name', 'father_name', 'parents_contact',
            'nok_name', 'nok_relationship', 'nok_contact',
            'nok_address', 'nok_date_of_birth',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nok_date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
