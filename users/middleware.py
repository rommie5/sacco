# middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

EXEMPT_URLS = [
    'login',            # name of your login view
    'register',         # name of your register view
    'admin:index',      # allow admin
    'complete_profile', # allow access to profile completion itself
]

class ProfileCompletionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None  # don't redirect if user is not logged in

        # Allow staff/admin to bypass
        if getattr(request.user, 'is_staff', False) or getattr(request.user, 'is_admin', False):
            return None

        try:
            profile = request.user.profile
        except Exception:
            return None  # user has no profile yet

        if not profile.is_completed:
            # current view name
            path_name = request.resolver_match.view_name if request.resolver_match else ''
            if path_name in EXEMPT_URLS:
                return None

            # allow static/media
            if request.path.startswith('/static/') or request.path.startswith('/media/'):
                return None

            # redirect to profile completion
            #return redirect('complete_profile')

        return None
