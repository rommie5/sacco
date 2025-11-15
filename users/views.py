from django.shortcuts import render,redirect
from django.contrib.auth import login,authenticate,logout
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm,CompleteProfileForm
from .models import MemberProfile
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from savings.models import SavingsAccount
import uuid
from . import signals
# Create your views here.

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            #Default role for public registration
            user.is_member = True
            user.is_admin = False
            user.is_auditor = False
            user.save()
            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {
        'form': form,
    })
#Login View with profile checks
@login_required
def login_view(request):
    form = UserLoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # ✅ Ensure profile exists
            member_profile = getattr(user, 'memberprofile', None)

            # ✅ Member but no profile yet → create one
            if user.is_member and member_profile is None:
                from .models import MemberProfile
                MemberProfile.objects.create(user=user)
                return redirect('completeprofile')

            # ✅ Member with incomplete profile
            if user.is_member and not member_profile.is_completed:
                return redirect('completeprofile')

            # ✅ Completed but waiting admin approval
            if user.is_member and not member_profile.is_approved:
                return redirect('pending_approval')

            # ✅ Approved users go to dashboard
            return redirect('dashboard')

        messages.error(request, "Invalid username or password")

    return render(request, 'registration/login.html', {'form': form})
    


#Pending approval view
@login_required
def pending_approval(request):
    # Refresh the user profile 
    profile = MemberProfile.objects.get(user=request.user)

    if profile.is_approved:
        return redirect('dashboard')
    
    # Still pending
    return render(request, 'users/pending.html', {'profile': profile})


def admin_dashboard(request):
    context = {
        "pending_approvals": MemberProfile.objects.filter(is_approved=False).count(),
        "active_members": MemberProfile.objects.filter(is_approved=True).count(),
    }
    return render(request, "users/admin.html", context)


def dashboard_view(request):
   
   
    # Get the user's savings account if it exists
    try:
        account = request.user.savings_account  # OneToOneField related_name
    except SavingsAccount.DoesNotExist:
        account = None

    context = {
        "account": account,
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def completeprofile(request):
    try:
        profile = request.user.memberprofile  # assuming OneToOne relation
    except MemberProfile.DoesNotExist:
        profile = MemberProfile(user=request.user)  # create if missing

    if request.method == 'POST':
        form = CompleteProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.is_completed = True
            profile.is_approved = False # ✅ must wait for admin approval
            profile.save()
            messages.success(request, "Profile submitted! Waiting approval.")
            return redirect('pending_approval')
    else:
        form = CompleteProfileForm(instance=profile)

    return render(request, 'users/completeprofile.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def profile_view(request):
    try:
        profile = MemberProfile.objects.get(user=request.user)
    except MemberProfile.DoesNotExist:
        #Create a profile if missing
        profile = MemberProfile.objects.create(
            user=request.user,
            national_id="N/A",
            phone_number="N/A",
            address="",
            membership_status="Pending"
        )

    return render(request, 'users/profile.html', {'profile': profile})