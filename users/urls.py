from django.urls import path
from . import views

urlpatterns=[
    path('register/',views.register_view,name='register'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('profile/',views.profile_view,name='profile'),
    path('dashboard/',views.dashboard_view,name='dashboard'),
    path('completeprofile/', views.completeprofile, name='completeprofile'),
    path('pending-approval/', views.pending_approval, name='pending_approval'),
    path('transactions/', views.transaction_history_view, name='transaction_history'),
    
    

]