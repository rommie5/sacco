from django.urls import path
from . import views

app_name = 'savings' 

urlpatterns = [
   # path('', views.dashboard, name='dashboard'),
    path('deposit/', views.deposit, name='deposit'),
   # path('deposit/create-intent/', views.create_stripe_intent, name='create_intent'),
    #path('success/', views.success, name='success'),
    path('', views.dashboard, name='savings_dashboard'),
    path('deposit/', views.deposit, name='savings_deposit'),
  
]
